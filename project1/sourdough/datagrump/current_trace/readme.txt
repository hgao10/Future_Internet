Our congestion control algorithm builds upon the basic AIMD algorithm and 
optimises it for cellular network following the  techniques developed in this 
paper https://arxiv.org/pdf/1807.02689.pdf  (page 3). In essence, we monitor 
the minimum RTT in a moving time window to better react to the fast link 
fluctuations in addition to AIMD. 