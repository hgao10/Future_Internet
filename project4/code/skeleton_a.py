# The MIT License (MIT)
#
# Copyright (c) 2019 Simon Kassing
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import networkx as nx
try:
    from . import wanteutility
except (ImportError, SystemError):
    import wanteutility

try:
    from . import assignment_parameters
except (ImportError, SystemError):
    import assignment_parameters

def solve(in_graph_filename, in_demands_filename, in_paths_filename, out_rates_filename):

    # Read in input
    graph = wanteutility.read_graph(in_graph_filename)
    demands = wanteutility.read_demands(in_demands_filename)
    all_paths = wanteutility.read_all_paths(in_paths_filename)
    paths_x_to_y = wanteutility.get_paths_x_to_y(all_paths, graph)
    all_flows = wanteutility.get_all_flows(all_paths, demands)

    final_rate={}
    #make a copy of the graph for updating weight
    new_graph=graph.copy()
    
    while(len(all_flows) !=0):
        edge_demand={}
        # all_flow_edges=[]
        #count the number of flows per link
        for demand_path in map(nx.utils.pairwise, all_flows):
            # each demand path is edge-constructed path with demand
            #for example path (0,1,4) -> [(0,1),(1,4)]
            
            #demand path can only be consumed once because it is created by map 
            # map returns a stateful iterator in Python 3. Stateful iterators may be 
            #only consumed once, after that it's exhausted and yields no values. Thus making a copy first
            demand_path_list= list(demand_path) 
            # all_flow_edges.append(demand_path_list)
            for edge in demand_path_list:
                if edge not in edge_demand.keys():
                    edge_demand[edge]=1
                else:
                    edge_demand[edge]+=1
        # print(all_flow_edges)
        #print("edge_demand:%s"%(edge_demand))
        edge_demand_reverse={}
        #calculate the min share per link
        for key, value in edge_demand.items():
            weight=new_graph.get_edge_data(*key)['weight']

            #set PRECISION to 4 digits
            # edge_demand[key] = "{:.4f}".format(weight/value)
            edge_demand_reverse["{:.4f}".format(weight/value)]=key
            #print("edge_demand_reverse:%s"%(edge_demand_reverse))
        #min_bw is now string
        min_bw = min([float(x) for x in edge_demand_reverse.keys()])
        
        min_bw_edge= edge_demand_reverse["{:.4f}".format(min_bw)]
        #print("min bw: %s and edge: %s"%(min_bw,min_bw_edge))
        #remove flows and links 
        remove_flows=[]
        for flow in all_flows:
            flow_edge=list(nx.utils.pairwise(flow))
            #print("per flow in edge form: %s"%(flow_edge))
            if min_bw_edge in flow_edge:
                #update flow rate per path 
                remove_flows.append(flow)
                final_rate[flow]=min_bw
                print("final rate: %s:%s"%(flow, min_bw))
                #update weight of all other edges in the flow
                for i in flow_edge:
                    if i != min_bw_edge:                
                        new_graph[i[0]][i[1]]['weight']=new_graph.get_edge_data(*i)['weight']-float(min_bw)
                        #print("Update edge %s weight : %s"%(i,new_graph[i[0]][i[1]]['weight']))

        all_flows= list(set(all_flows)-set(remove_flows))
        #print(all_flows)
        #print(final_rate)

    # Finally, write the rates to the output file
    with open(out_rates_filename, "w+") as rate_file:
        for path in all_paths:
            if path not in final_rate.keys():
                rate_file.write("0\n")
            else:
                rate_file.write("%s\n"%(final_rate[path]))


def main():
    for appendix in range(assignment_parameters.num_tests_a):
        solve(
            "../ground_truth/input/a/graph%s.graph" % appendix,
            "../ground_truth/input/a/demand%s.demand" % appendix,
            "../ground_truth/input/a/path%s.path" % appendix,
            "../myself/output/a/rate%s.rate" % appendix
        )
    # appendix = 5
    # solve(
    #     "../ground_truth/input/a/graph%s.graph" % appendix,
    #     "../ground_truth/input/a/demand%s.demand" % appendix,
    #     "../ground_truth/input/a/path%s.path" % appendix,
    #     "../myself/output/a/rate%s.rate" % appendix
    # )


if __name__ == "__main__":
    main()
