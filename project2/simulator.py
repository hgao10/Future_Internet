import os
import pandas as pd
from experiment import experiment

BANDWIDTH_TRACE = 'bandwidth_trace/'
VIDEO_TRACE = 'video_trace/'

Mbs_to_Bps = 1000000./8

def main():
    experiments = {}
    video = []

    for fn in os.listdir(BANDWIDTH_TRACE):
        df = pd.read_csv(BANDWIDTH_TRACE+fn, delimiter=' ', header=None)
        experiments[fn] = {
            'time': df[0].tolist(),
            'bandwidth': (df[1]*Mbs_to_Bps).tolist(),
        }

    for fn in sorted(os.listdir(VIDEO_TRACE)):
        df = pd.read_csv(VIDEO_TRACE+fn, header=None)
        video.append(df[df.columns[0]].tolist())

    total_reward = 0.
    write_data = []
    for exp in experiments:
        reward, rebuffer_time, switches_amplitude = experiment(
            exp,
            experiments[exp]['time'],
            experiments[exp]['bandwidth'],
            video
        )
        total_reward += reward
        write_data.append((exp, reward, rebuffer_time, switches_amplitude))

    with open('logs/log.csv','w') as f:
        f.write('log_name,reward,rebuffer_time,switches_amplitude\n')
        for x in write_data:
            f.write('%s,%f,%f,%f\n'%(x))

    print('Total reward:', total_reward)

if __name__ == '__main__':
    main()