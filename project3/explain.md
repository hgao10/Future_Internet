We used greedy algorithm to compute the satellite links. For each hop, we consider
all satellites excluding the ones that are already on the chosen path and the ones that have
reached 4 isls. Then we compute the distance between the candidates and the destination.
Last, we pick the satellite that is closest to the destination for each hop. For optimization,
we tried to randomize the city pairs and used the one ordering that gives us the minimal score. 