# Future Internet - Adaptive bitrate streaming

## Introduction

Video streaming services want to provide the highest possible video quality without causing video stalling under various network conditions.

Video providers have every video stored in multiple quality levels (e.g. 360p, 1080p, 4k). Intuitively, each quality level requires proportional network bandwidth. Under ideal network conditions (i.e. constant bandwidth), there is no need for adaptive delivery. However, when bandwidth changes are very common, for example with mobile devices using cellular networks, we want to deliver video adaptively and change video quality depending on network conditions.

Each video is divided into chunks. In this assignment, we assume that every chunk has a constant duration of 4 seconds. All video chunks are available in 6 quality levels. We have to decide which chunk to fetch.  Each quality level (approximately) requires the following network bandwidth:

```
300Kbps, 750Kbps, 1200Kbps, 1850Kbps, 2850Kbps, 4300Kbps
```

Your task is to design an algorithm for video delivery: adaptive bitrate streaming (ABR) algorithm.

You algorithm is evaluated using real-world traces collected on mobile devices.

User experience is negatively affected by two types of events (1) video stops (rebuffering), and (2) frequent changes in video quality. The optimization goal of this exercise takes these two tasks into account:

```
score = agg_video_bitrate - 4.3 * rebuffer_time - agg_switches_amplitude

agg_video_bitrate - sum of all chunk bitrates across all traces
rebuffer_time - aggregated rebuffering time across all traces
agg_switches_amplitude - aggregated differences of consecutive chunk bitrates across all traces
```

## Setup

You implement your ABR algorithm by modifying the _abr.py_. To test your soulution, run:

```bash
python simulator.py
```

The _simulator.py_ script will run your solution against multiple network traces and as result, it prints the final score.

## Submit your solution

After you successfully execute simulator.py, the _log.csv_ file is created in the _logs_ folder. After you commit this file, your score on the leader board will be updated.

### Task 1

Achieving score **5000** will give you at least 4 points.

### Task 2

Achieving the score **5500** will give you at least 8 points.

### Task 3
Optimize your solution to reach the top of the leader board.

### Related literature

Rate Adaptation for Adaptive HTTP Streaming (SIGCOMM 2011)
A Buffer-Based Approach to Rate Adaptation: Evidence from a Large Video Streaming Service (SIGCOMM 2014)
Neural Adaptive Video Streaming with Pensieve (SIGCOMM 2017)

### Final notice
The maximum number of points is _12.5_.

In you algorithm, **do not hardcode network traces**. You can make decision based on the bandwidth you have observed, but not based on the bandwidth changes that will come in the future. 

Before the deadline, write a short _readme_ (up to 5 sentences) about how your algorithm works and store it in:

```
explain.md
```

**You can find the leader board [here](http://bach20.ethz.ch/abr_contest.html)**
