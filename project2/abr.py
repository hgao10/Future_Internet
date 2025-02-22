def last_chunk_number(n):
    last_chunk_number.value = n

def get_last_chunk():
    return last_chunk_number.value

def set_last_buffer(n):
    set_last_buffer.value = n

def get_last_buffer():
    return set_last_buffer.value

def set_startup_phase(n):
    set_startup_phase.value = n

def get_startup_phase():
    return set_startup_phase.value

def get_downloadchunk():
    return set_downloadchunk.value

def set_downloadchunk(n):
    set_downloadchunk.value = n

def get_download_starttime():
    return set_download_starttime.value

def set_download_starttime(n):
    set_download_starttime.value = n




def abr(
    typ,
    current_time,
    playback_time,
    playback_chunk,
    current_chunk,
    current_chunk_quality,
    current_chunk_download,
    video
):
    """
        typ - type of event
            0 - initial call at time 0
            1 - a chunk has been downloaded
            2 - timeout has happend
            3 - rebuffering started
        
        current_time - time from the beginning of the simulation in seconds
        
        playback_time - how much of the video has been shown (in seconds)
            - if there was no rebuffering, playback_time is the same as current_time
        playback_chunk - the chunk that is playing right now
        
        current_chunk - the chunk number that is downloading right now (or has been just finished)
        current_chunk_quality - the quality of the current_chunk
        current_chunk_download - how much of current_chunk has been downloaded (in bytes)
        video - contains 6 video arrays (one per quality level). 
            - Each subarray contain the size of each chunk in the video

        Returns
            quality_to_download_now, chunk_to_download_now, timeout

        ABR function returns the next chunk that should be downloaded
            quality_to_download_now - quality of the next chunk from 0 to 5
            chunk_to_download_now - chunk number of the chunk that should be downloaded
                - next_chunk cannot be in the past, if the player plays chunk 10, chunk 9 shouldn't be downloaded
                - if you set next_chunk to -1, no chunk will be downloaded
                - if the previou download hasn't been completed (e.g. in case of rebuffering) you can change the chunk
                that is currently downloading. For instance, you started downloading a high quality chunk, but
                rebuffering happened and now you would like to lower the quality. In that case, return the same chunk
                number, but different quality.
            timeout - set a timer that will trigger the abr function again
                - timeout is in absolute time, usually set it as current_time+X (where min X is 200ms)
                - timeout 0 means no timeout
    """
    # video_t = []
    # for x in video:
    #     video_t += x

    # video_min = min(video_t)
    # video_max = max(video_t)

    # print("video_min: %s, video_max: %s" %(video_min, video_max))

    timeout = 1000000
    download_time = 1000
    print("ABR invoke type :%s\n" % typ)
    if(typ == 1):
        print("ABR: call because a chunk has been downloaded, current_chunk: %s, size: %s, downloaded:%s\n" %
            (current_chunk,video[current_chunk_quality][current_chunk], current_chunk_download ))
        if(current_chunk == get_downloadchunk()):
            download_time = current_time - get_download_starttime()
            set_download_starttime(current_time)
            set_downloadchunk(current_chunk+1)

    if(typ == 0):
        last_chunk_number(0) 
        set_last_buffer(0)
        set_startup_phase(True)
        set_downloadchunk(0)
        set_download_starttime(current_time)
        print("type 0, startup phase set to trune :%s\n"%(get_startup_phase()))
        return 0,0,current_time + timeout
    elif(typ == 3):
        print("type 3 rebuffering, current_chunk: %s\n" %(current_chunk))
        return 0,current_chunk, current_time + timeout
    elif(current_chunk == -1):
        print("return cause current chunk == -1")
        return 0, current_chunk,0
    # elif(current_chunk + 1 == len(video[0])):
    #     print("return as current chunk is the last one, current_chunk_download : %s, current_chunk size: %s\n" %(current_chunk_download,
    #         video[current_chunk_quality][current_chunk]))
    #     return 0, current_chunk , current_time+timeout


    if(current_chunk != -1):
        next_chunk = current_chunk+1
    else:
        next_chunk = get_last_chunk()+1

    # only overwrite previous state if current_chunk is a valid chunk
    if(current_chunk != -1):
        last_chunk_number(next_chunk)

    #if we arrived to the end of the stream or it is not the initial call and the download has finished
    if next_chunk == len(video[0]):
        next_chunk = -1


    print("next chunk= %d" %(next_chunk))
    startup_period = 100
    buffer_startup_scale = 0.875

    chunk_size = 4 # seconds
    reservoir_size = 9   # seconds
    cushion_size = 43 # seconds
    buffer_size = chunk_size * (current_chunk - playback_chunk) # seconds
    
    buffer_delta = buffer_size - get_last_buffer()
    set_last_buffer(buffer_size)
    print("buffer_delta: %s\n" %(buffer_delta))
    
    rate_next_startup = 0
    # calculate rate during stateup phase
    if (current_time <= startup_period and get_startup_phase() == True):
        #if (buffer_delta > 4 * buffer_startup_scale):
        #threshold_scale = float(-6/(cushion_size+reservoir_size))
     
        threshold_scale=float( -0.0115 *float(buffer_size)) + float(9)
        print("ABR: startup phase threshold_scale %f,buffer_size: %s, download_time: %s\n" %(threshold_scale, buffer_size, download_time))
        if(download_time < 4/threshold_scale):
            print("download time meets the threshold, increase")
            rate_next_startup = min(current_chunk_quality+1,5)


    # if (buffer_delta < 0 and get_startup_phase() != False):  
    #     set_startup_phase(False)
    #     print("set startup phase to false %s due to buffer decreasing\n" %(get_startup_phase()))

    rate_next = 0
    print("buffer_size = %d" %buffer_size)
    rate_val = get_rate(buffer_size, reservoir_size, cushion_size)
    print("rate_val = %d" %rate_val)

    rates = [300, 750, 1200, 1850, 2850, 4300]
    current_rate = rates[current_chunk_quality]
    # determine next rates to possibly choose
    if(current_chunk_quality == 5):
        R_plus = video[current_chunk_quality][current_chunk]
    else:
        #R_plus = min([x for x in rates if x > current_rate])
        R_plus = video[current_chunk_quality+1][current_chunk]

    if(current_chunk_quality == 0):
        R_minus = video[current_chunk_quality][current_chunk]
    else:
        #R_minus = max([x for x in rates if x < current_rate]) 
        R_minus = video[current_chunk_quality-1][current_chunk]
    
    if(buffer_size < reservoir_size):
        print("buffer size < reserv. size")
        rate_next = 0
    elif(buffer_size >= (reservoir_size + cushion_size)):
        print("maximal rate")
        rate_next = 5
    elif(rate_val >= R_plus):
        print("choose R_plus")
        # video[quality][chunk_num]
        #rate_next = max([x for x in [0,1,2,3,4,5] if rates[x] < rate_val])
        if (next_chunk != -1):
            rate_next = max([x for x in [0,1,2,3,4,5] if video[x][current_chunk+1] < rate_val])
        else: 
            rate_next = max([x for x in [0,1,2,3,4,5] if video[x][0] < rate_val])
        print("rate_next for R_plus: %s\n" %(rate_next))

    elif(rate_val <= R_minus):
        print("choose R_minus")
        if (next_chunk != -1):
            rate_next = min([x for x in [0,1,2,3,4,5] if video[x][current_chunk+1] > rate_val])
        else:
            rate_next = min([x for x in [0,1,2,3,4,5] if video[x][0] > rate_val])

        print("rate_next for R_minus: %s\n" %(rate_next))
    else:
        print("stay at current rate")
        rate_next = current_chunk_quality
    
    if (rate_next > rate_next_startup and get_startup_phase() != False):
        set_startup_phase(False)
        print("chunk map rate is greater than startup rate, set startup phase to False: %s\n" %(get_startup_phase()))

    rate_next = max(rate_next, rate_next_startup)
    print("rate_next: %s, next_chunk: %s, current_time+timeout: %s\n" %(rate_next, next_chunk, current_time+timeout) )
    return rate_next, next_chunk, current_time + timeout # after 4s check again

def get_rate(buffer_size, reservoir_size, cushion_size):
    return ((2395588 - 111155)/cushion_size) * (buffer_size - reservoir_size) + 111155

