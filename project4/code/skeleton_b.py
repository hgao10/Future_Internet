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

try:
    from . import wanteutility
except (ImportError, SystemError):
    import wanteutility

try:
    from . import assignment_parameters
except (ImportError, SystemError):
    import assignment_parameters

import networkx as nx

class FlowRate():
    def __init__(self,name, path):
        self.name = "r"+ str(name)
        self.path = path
        self.edges = list(nx.utils.pairwise(path)) # a list of edge tuples contained in the path
    def name(self):
        return self.name
    def path(self):
        return self.path
    def edges():
        return self.edges

def solve(in_graph_filename, in_demands_filename, in_paths_filename, out_rates_filename):

    # Read in input
    graph = wanteutility.read_graph(in_graph_filename)
    demands = wanteutility.read_demands(in_demands_filename)
    all_paths = wanteutility.read_all_paths(in_paths_filename)
    paths_x_to_y = wanteutility.get_paths_x_to_y(all_paths, graph)
    all_flows = wanteutility.get_all_flows(all_paths, demands) # paths that have demands

    edges_demand = {}
    flows_demand= {}
    path_rate_name = {} # key: flow name r1, r2 , value: path (0,1,2)
    final_rate={} # key: path, value: flow rate result from LP resolver 
    # Write the linear program
    with open("../myself/output/b/program.lp", "w+") as program_file:
        #example        max: x1 - x2;
                        # x1 >= 0.3;
                        # x1 <= 30.6;
                        # x2 >= 24.9;
                        # x2 <= 50.1;

        # write objective function
        program_file.write("max: Z; \n")

        # for each flow with demand, create a FlowRate object
        flowrate=[]
        for flow in all_flows:
            flowrate.append(FlowRate(all_flows.index(flow), flow))
            path_rate_name[flowrate[-1].name]=flowrate[-1].path

        # constraint 1: path rate > 0
        for f in flowrate:
            program_file.write("%s > 0.0; \n" %(f.name))

            # populate edge dictionary:
            for e in f.edges:
                if e not in edges_demand.keys():
                    edges_demand[e] = [f.name]
                else:
                    edges_demand[e].append(f.name)

            #populate flow dictionary (including all paths)
            if (f.path[0],f.path[-1]) not in flows_demand.keys():
                flows_demand[(f.path[0],f.path[-1])] = [f.name]
            else:
                flows_demand[(f.path[0],f.path[-1])].append(f.name)

        # print("edges demand: %s \n"%(edges_demand))
        # print("flows_demand %s \n"%(flows_demand))
        # constraint 2: can not exceed link capacities
        for key, value in edges_demand.items():
            weight = graph.get_edge_data(*key)['weight']
            if len(value) < 2:
                program_file.write("%s <= %s; \n" %( value[0], weight))
            else:
                program_file.write("%s <= %s; \n" %( "+".join(value), weight))

        # constrant 3: each flow (all paths) > Z
        for i in flows_demand.values():
            if len(i) < 2:
                program_file.write("%s - Z > 0.0; \n"%(i[0]))
            else:
                program_file.write("%s -Z > 0.0; \n"%("+".join(i)))


    # Solve the linear program
    var_val_map = wanteutility.ortools_solve_lp_and_get_var_val_map(
        '../myself/output/b/program.lp'
    )

    # Retrieve the rates from the variable values
    print("var_val_map :%s" %(var_val_map))
    for key, value in var_val_map.items():
        if key != 'Z':
            # its a flow rate
            final_rate[path_rate_name[key]]=value

    # print("path_rate_name: %s\n" %(path_rate_name))
    # print("final_rate: %s\n" %(final_rate))
    # Finally, write the rates to the output file
    with open(out_rates_filename, "w+") as rate_file:
        for path in all_paths:
            if path not in final_rate.keys():
                rate_file.write("0\n")
            else:
                rate_file.write("%s\n"%(final_rate[path]))


def main():
    for appendix in range(assignment_parameters.num_tests_b):
        solve(
            "../ground_truth/input/b/graph%s.graph" % appendix,
            "../ground_truth/input/b/demand%s.demand" % appendix,
            "../ground_truth/input/b/path%s.path" % appendix,
            "../myself/output/b/rate%s.rate" % appendix
        )
    # appendix=2
    # solve(
    #     "../ground_truth/input/b/graph%s.graph" % appendix,
    #     "../ground_truth/input/b/demand%s.demand" % appendix,
    #     "../ground_truth/input/b/path%s.path" % appendix,
    #     "../myself/output/b/rate%s.rate" % appendix
    # )



if __name__ == "__main__":
    main()
