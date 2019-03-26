import abr

SEGMENT_LENGTH = 4.
inf = 100000000.

BITRATES = [300, 750, 1200, 1850, 2850, 4300] #Kbps

def call_abr(typ, state):
    nxt_quality, nxt_chunk, timeout = abr.abr(
        typ,
        state['time'],
        state['playback_time'],
        state['playback_chunk'],
        state['next_chunk'],
        state['next_chunk_quality'],
        state['next_chunk_downloaded'],
        state['video']
    )
    assert nxt_chunk == -1 or (nxt_chunk > state['playback_chunk'] and nxt_chunk < len(state['video'][0]))
    assert 0 <= nxt_quality <= 5
    assert timeout >= 0
    if timeout == 0:
        timeout = inf
    elif timeout != state['timeout']:
        assert timeout - state['time']>= 0.199
    assert timeout>state['time']
    return nxt_quality, nxt_chunk, timeout

def set_timeout(state, timeout):
    if timeout == 0:
        timeout = inf
    elif timeout != state['timeout']:
        assert timeout - state['time']>= 0.199
    assert timeout>state['time']
    state['timeout'] = timeout

def set_download(state, nxt_quality, nxt_chunk, timeout):
    state['timeout'] = timeout
    if nxt_chunk == -1:
        state['next_chunk'] = -1
        state['next_chunk_quality'] = 0
        state['next_chunk_downloaded'] = 0
        state['next_chunk_expected'] = inf
    else:
        state['next_chunk'] = nxt_chunk
        state['next_chunk_quality'] = nxt_quality
        state['next_chunk_downloaded'] = 0
        state['next_chunk_expected'] = state['video'][nxt_quality][nxt_chunk]/state['bandwidth']+state['time']

def experiment(exp_name, time_trace, bandwidth_trace, video):
    state = {
        'bandwidth': bandwidth_trace[0],
        'time': 0.,
        'video': video,

        'total_video_duration': len(video[0])*SEGMENT_LENGTH,
        'data': [-1]*len(video[0]),

        'playback_time': 0.,
        'playback_chunk': -1,
        'playback_change_time': inf,
        'rebuffering': True,

        'next_chunk': -1,
        'next_chunk_quality': -1,
        'next_chunk_downloaded': -1.,
        'next_chunk_expected': -1.,

        'timeout': inf
    }

    #drop first change
    del time_trace[0]
    del bandwidth_trace[0]

    #init abr, start downloading the first chunk
    nxt_quality, nxt_chunk, timeout = call_abr(0, state)
    set_download(state, nxt_quality, nxt_chunk, timeout)

    while True:
        trace_min = inf if len(time_trace) == 0 else time_trace[0]
        min_time = min(
            state['playback_change_time'],
            state['next_chunk_expected'],
            state['timeout'],
            trace_min
        )

        if min_time != state['time']:
            #update progress
            time_diff = min_time - state['time']
            state['time'] = min_time

            if state['playback_chunk'] != -1:
                #if the playback started
                state['playback_time'] += time_diff

            state['next_chunk_downloaded'] += time_diff*state['bandwidth']

        if min_time == state['playback_change_time']:
            #rebuffering or reading the next chunk
            if state['playback_chunk'] + 1 == len(video[0]):
                #end of the video
                break

            if state['data'][state['playback_chunk']+1] != -1:
                state['playback_chunk'] += 1
                state['playback_change_time'] = state['time'] + SEGMENT_LENGTH
                state['rebuffering'] = False
            else:
                state['rebuffering'] = True
                state['playback_change_time'] = inf
                nxt_quality, nxt_chunk, timeout = call_abr(3, state)
                # if the user wants to change the decision
                if nxt_quality != state['next_chunk_quality'] or nxt_chunk != state['next_chunk']:
                    # download the next chunk
                    set_download(state, nxt_quality, nxt_chunk, timeout)
                else:
                    set_timeout(state, timeout)
        elif min_time == state['next_chunk_expected']:
            #chunk downloaded

            #if the new chunk is not already playing
            if state['next_chunk'] != state['playback_chunk']:
                state['data'][state['next_chunk']] = state['next_chunk_quality']
                #play video if it was blocked
                if state['rebuffering'] and state['playback_chunk']+1 == state['next_chunk']:
                    state['playback_chunk'] += 1
                    state['playback_change_time'] = state['time'] + SEGMENT_LENGTH
                    state['rebuffering'] = False

            nxt_quality, nxt_chunk, timeout = call_abr(1, state)
            set_download(state, nxt_quality, nxt_chunk, timeout)

        elif min_time == trace_min:
            #bandwidth change
            bandwidth = bandwidth_trace[0]
            del time_trace[0]
            del bandwidth_trace[0]

            state['bandwidth'] = bandwidth
            if state['next_chunk'] != -1:
                state['next_chunk_expected'] = (video[state['next_chunk_quality']][state['next_chunk']] - state['next_chunk_downloaded'])/state['bandwidth']+state['time']
        elif min_time == state['timeout']:
            #call abr with the timeout option
            nxt_quality, nxt_chunk, timeout = call_abr(2, state)
            # if the user wants to change the decision
            if nxt_quality != state['next_chunk_quality'] or nxt_chunk != state['next_chunk']:
                # download the next chunk
                set_download(state, nxt_quality, nxt_chunk, timeout)
            else:
                set_timeout(state, timeout)

    switches_amplitude = sum(abs(BITRATES[state['data'][i-1]]-BITRATES[state['data'][i]]) for i in range(len(state['data'])))
    rebuffer_time = state['time'] - len(video[0])*SEGMENT_LENGTH
    quality = sum(map(lambda x: BITRATES[x], state['data']))

    REBUF_PENALTY = 4.3  # 1 sec rebuffering -> 3 Mbps
    SMOOTH_PENALTY = 1
    M_IN_K = 1000.0
    score = quality / M_IN_K - REBUF_PENALTY * rebuffer_time - SMOOTH_PENALTY * switches_amplitude / M_IN_K

    return score, rebuffer_time, switches_amplitude