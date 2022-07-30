import os
import time
from typing import List, Any, Callable, List, Optional
from functools import wraps

from psycopg2 import connect, sql

import matplotlib.pyplot as plt
import networkx as nx

from annotations import *

import random


def get_tree_node_pos(
    G, root=None, width=1.0, height=1, vert_gap=0.1, vert_loc=0, xcenter=0.5
):

    """
    From Joel's answer at https://stackoverflow.com/a/29597209/2966723.
    Licensed under Creative Commons Attribution-Share Alike
    If the graph is a tree this will return the positions to plot this in a
    hierarchical layout.
    G: the graph (must be a tree)
    root: the root node of current branch
    - if the tree is directed and this is not given,
      the root will be found and used
    - if the tree is directed and this is given, then
      the positions will be just for the descendants of this node.
    - if the tree is undirected and not given,
      then a random choice will be used.
    width: horizontal space allocated for this branch - avoids overlap with other branches
    vert_gap: gap between levels of hierarchy
    vert_loc: vertical location of root
    xcenter: horizontal location of root
    """
    if not nx.is_tree(G):
        raise TypeError(
            "cannot use hierarchy_pos on a graph that is not a tree"
        )

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(
                iter(nx.topological_sort(G))
            )  # allows back compatibility with nx version 1.11
        else:
            root = random.choice(list(G.nodes))

    path_dict = dict(nx.all_pairs_shortest_path(G))
    max_height = 0
    for value in path_dict.values():
        max_height = max(max_height, len(value))
    vert_gap = height / max_height

    def _hierarchy_pos(
        G,
        root,
        width,
        vert_gap,
        vert_loc,
        xcenter,
        pos=None,
        parent=None,
        min_dx=0.05,
    ):
        """
        see hierarchy_pos docstring for most arguments
        pos: a dict saying where all nodes go if they have been assigned
        parent: parent of this branch. - only affects it if non-directed
        """

        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children) != 0:
            dx = max(min_dx, width / len(children))
            nextx = xcenter - width / 2 - max(min_dx, dx / 2)
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(
                    G,
                    child,
                    width=dx,
                    vert_gap=vert_gap,
                    vert_loc=vert_loc - vert_gap,
                    xcenter=nextx,
                    pos=pos,
                    parent=root,
                )
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


def clean_up_static_dir(ignore_list: List[str]):
    static_dir = os.path.join(project_root, "static")
    for filename in os.listdir(static_dir):
        if (
            filename.startswith("graph_") and filename not in ignore_list
        ):  # not to remove other images
            os.remove(os.path.join(static_dir, filename))
            
            
class Node:
        
    def __init__(self, query_plan, curr_node, count):
        self.count = count
        self.parent = curr_node
        self.node_type = query_plan["Node Type"]
        self.cost = query_plan["Total Cost"]
        self.parent_relationship = query_plan.get("Parent Relationship")
        self.relation = query_plan.get("Relation Name")
        self.alias = query_plan.get("Alias")
        self.startup_cost = query_plan.get("Startup Cost")
        self.plan_rows = query_plan.get("Plan Rows")
        self.plan_width = query_plan.get("Plan Width")
        self.filter = query_plan.get("Filter")
        self.raw_json = query_plan
        self.name = self.getName()
        self.explanation = self.create_explanation(query_plan, self)
        
    def getNodeType(self):
        return self.node_type
    
    def getRelation(self):
        return self.relation
        

    def __str__(self):
        name_string = f"{self.node_type}\ncost: {self.cost}"
        return name_string

    # creates explaination by calling explainer map in annotations.py
    @staticmethod
    def create_explanation(query_plan, node):
        ex = explainer_map(query_plan, node)
        return ex

    def has_children(self):
        return "Plans" in self.raw_json
    
    # assigns a unique name eg T1, T2 etc.
    def getName(self):
        if not self.has_children() == None:
            return "T" + str(self.count)
        return None
    
    # gets unique name
    def get(self):
        return self.name
    
    # get name of parent node (parent query plan) (used in explainations in annotations.py)
    def getParent(self):
        if type(self.parent) == str:
            return self.name
        else:
            return self.parent.get()
    
    
    
class QueryPlan:
    """
    A query plan is a directed graph made up of several Nodes
    """

    def __init__(self, query_json, raw_query):
        global count
        count =0
        self.graph = nx.DiGraph()
        self.root = Node(query_json, " ", count)
        self._construct_graph(self.root, count)
        self.raw_query = raw_query

    # recursive function to loop through json query execution plan and get the plan at each time
    def _construct_graph(self, curr_node, count):
        count +=1
        self.graph.add_node(curr_node)
        if curr_node.has_children(): # iterates through the children
            for child in curr_node.raw_json["Plans"]: # creates child nodes
                child_node = Node(child, curr_node, count)
                self.graph.add_edge(
                    curr_node, child_node
                )  # add both curr_node and child_node if not present in graph
                count+=1
                self._construct_graph(child_node, count) 
                

    def save_graph_file(self):
        '''
        saves graph as an image in png in local directory
        '''
        graph_name = f"graph_{str(time.time())}.png"
        filename = os.path.join(os.getcwd(), graph_name)
        plot_formatter_position = get_tree_node_pos(self.graph, self.root)
        node_labels = {x: str(x) + "\n" + x.get() for x in self.graph.nodes}
        plt.figure(1,figsize=(10,10)) 
        nx.draw(
            self.graph,
            plot_formatter_position,
            with_labels=True,
            labels=node_labels,
            font_size=9,
            node_size=5000,
            node_color="skyblue",
            node_shape="s",
            alpha=1,
        )
        plt.savefig(filename)
        plt.clf()
        return graph_name

    def create_explanation(self, node: Node):
        if not node.has_children:
            return [node.explanation]
        else:
            result = []
            for child in self.graph[node]:
                result += self.create_explanation(child)
            result += [node.explanation]
            return result

class QueryRunner:
    def __init__(self, pwd, hostname = 'localhost', database = 'TPC-H', username = 'postgres', port_id ="5432"):
        self.dbname=database
        self.user=username
        self.password=pwd
        self.host=hostname
        self.port=port_id
        self.conn = self.set_up_db_connection()
        self.cursor = self.conn.cursor()

    # connects to database
    def set_up_db_connection(self):
        try:
            return connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )
        except:
            return "Could not connect to database."

    def tear_down_db_connection(self):
        self.conn.close()
        self.cursor.close()

    # main function called by interface to generate query execution plan
    def explain(self, query: str) -> QueryPlan:
        self.cursor.execute("EXPLAIN (FORMAT JSON) " + query)
        plan = self.cursor.fetchall()
        query_plan_dict: dict = plan[0][0][0]["Plan"]
        return QueryPlan(query_plan_dict, query)

   