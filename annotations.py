def aggregate(query_plan, node):
    # For plans of the aggregate type: SortAggregate, HashAggregate, PlainAggregate
    strategy = query_plan["Strategy"]
    if strategy == "Sorted":
        result = f"The rows of {node.get()} are sorted based on their keys."
        if "Group Key" in query_plan:
            result += " It aggregated by the following keys: "
            for key in query_plan["Group Key"]:
                result += key + ","
            result = result[:-1]
            result += "."
        if "Filter" in query_plan:
            result += " They are filtered by " + query_plan["Filter"].replace("::text", "")
            result += "."
        return result
    elif strategy == "Hashed":
        result = f"It hashes all rows of {node.get()} based on the following key(s): "
        for key in query_plan["Group Key"]:
            result += key.replace("::text", "") + ", "
        result += f"which are then aggregated into bucket given by the hashed key to produce {node.getParent()}"
        return result
    elif strategy == "Plain":
        return f"{node.get()} is simply aggregated as normal to produce {node.getParent()}"
    else:
        raise ValueError(
            "Aggregate_explain does not work for strategy: " + strategy
        )
        
def append_explain(query_plan, node):
    result = f"This plan runs multiple sub-operations on {node.get()}'s children, and returns all the rows that were returned as one result set to produce {node.get()}"
    return result

def values_scan_explain(query_plan, node):
    result = f"A values scan on {node.get()}'s child operation is done using the given values from the query to produce {node.get()}"
    return result

def unique_explain(query_plan, node):
    result = f"Using the sorted data from the sub-operations, a scan is done on each row of {node.get()} and only unique values are preserved to produce {node.get()}"
    return result

def subquery_scan_explain(query_plan, node):
    result = f"Subquery scan is done on results of {node.get()} from sub-operations but there are no changes."
    return result

def sort_explain(query_plan, node):
    result = f"{node.get()} is sorted using the attribute "
    if "DESC" in query_plan["Sort Key"]:
        result += (
            str(query_plan["Sort Key"].replace("DESC", "")))+ " in descending order"
        
    elif "INC" in query_plan["Sort Key"]:
        result += (
            str(query_plan["Sort Key"].replace("INC", ""))) + " in increasing order"
        
    else:
        result += str(query_plan["Sort Key"])
    result += f"to produce {node.get()}."
    return result

def setop_explain(query_plan, node):
    # https://www.depesz.com/2013/05/19/explaining-the-unexplainable-part-4/
    result = "It finds the "
    cmd_name = str(query_plan["Command"])
    if cmd_name == "Except" or cmd_name == "Except All":
        result += "differences "
    else:
        result += "similarities "
    result += "between the two previously scanned tables using the {} operation.".format(
        query_plan["Node Type"])
    

    return result

def seq_scan_explain(query_plan, node):
    sentence = f"It does a sequential scan on relation "
    if "Relation Name" in query_plan:
        sentence += query_plan["Relation Name"]
    if "Alias" in query_plan:
        if query_plan["Relation Name"] != query_plan["Alias"]:
            sentence += " with an alias of {}".format(query_plan["Alias"])
    if "Filter" in query_plan:
        sentence += " and filtered with the condition {}".format(
            query_plan["Filter"].replace("::text", "")
        )
    sentence += f"to produce {node.get()}."

    return sentence

def nested_loop_explain(query_plan, node):
    result = f"The join results between the nested loop scans of the suboperations are returned as new rows to produce {node.get()}"
    return result

def merge_join_explain(query_plan, node):
    result = f"The results from sub-operations are joined using Merge Join "

    if "Merge Cond" in query_plan:
        result += " with condition " + query_plan["Merge Cond"].replace("::text", "")
        

    if "Join Type" == "Semi":
        result += " but only the row from the left relation is returned"

    result += f"to produce {node.get()}."
    return result

def materialize_explain(query_plan, node):
    # https://www.depesz.com/2013/05/09/explaining-the-unexplainable-part-3/
    result = "The results of sub-operations are stored in memory for faster access."
    return result

def limit_explain(query_plan, node):
    # https://www.depesz.com/2013/05/09/explaining-the-unexplainable-part-3/
    result = f"Instead of scanning the entire table {node.get()}, the scan is done with a limit of {query_plan['Plan Rows']} entries to produce {node.getParent()}"
    return result


def index_only_scan_explain(query_plan, node):
    result = ""
    result += f"An index scan is done using an index table " + query_plan["Index Name"]
    
    if "Index Cond" in query_plan:
        result += " with condition(s) " +  query_plan["Index Cond"].replace("::text", "")
        
    result += ". It then returns the matches found in index table scan as the result."
    if "Filter" in query_plan:
        result += (
            " The result is then filtered by " + query_plan["Filter"].replace("::text", ""))+ "."
        
    result += f"to produce {node.get()}."
    return result

def index_scan_explain(query_plan, node):
    result = ""
    result +=  f"An index scan is done on {node.get()} using an index table " + query_plan["Index Name"]
    
    if "Index Cond" in query_plan:
        result += " with the following conditions: " +  query_plan["Index Cond"].replace("::text", "")
        
    result += ", and the {} table and fetches rows pointed by indices matched in the scan.".format(
        query_plan["Relation Name"])
    

    if "Filter" in query_plan:
        result += " The result is then filtered by "+ query_plan["Filter"].replace("::text", "")+ "."
      
    result += f"to produce {node.getParent()}."
    return result

def hash_join_explain(query_plan, node):
    result = ""
    result += f"The result from previous operation is joined using Hash {query_plan['Join Type']} {'Join'}"
    if "Hash Cond" in query_plan:
        result += " on the condition: {}".format(
            query_plan["Hash Cond"].replace("::text", ""))
        
    result += f"to produce {node.getParent()}."
    return result


def hash_explain(query_plan, node):
    result = f"The hash function makes a memory hash with rows from {node.get()}'s children (see graph) to produce {node.get()}"
    return result


def group_explain(query_plan, node):
    result = f"The result from the previous operation is grouped together using the following keys: "
    for i, key in enumerate(query_plan["Group Key"]):
        result += key.replace("::text", "")
        if i == len(query_plan["Group Key"]) - 1:
            result += "."
        else:
            result += ", "
    result += f"to produce {node.getParent()}."      
    return result


def function_scan_explain(query_plan, node):
    return "The function {} is run and returns the recordset created by it.".format(
        query_plan["Function Name"])

def default_explain(query_plan, node):
    return "The {} is performed.".format(query_plan["Node Type"])


def cte_explain(query_plan, node):
    result =f"A CTE scan is performed on the table "+ str(query_plan["CTE Name"])+ " which is stored in memory "
    
    if "Index Cond" in query_plan:
        result += " with condition(s) " + query_plan["Index Cond"].replace("::text", "")
        
    if "Filter" in query_plan:
        result += " and then filtered by " + query_plan["Filter"].replace("::text", "")
        
    result += f"to produce {node.getParent()}."
    return result

def test_explain(query_plan, node):
    # Just for testing
    return "Test"

def gather_merge_explain(query_plan, node):
    result =f"Gather Merge is performed on the table {node.get()} to get {node.getParent()}"
    return result
    
def memoize_explain(query_plan, node):
    # https://blog.jonudell.net/2021/08/19/postgres-set-returning-functions-that-self-memoize-as-materialized-views/
    result =f"Results stored using memoization on the table {node.get()} to get {node.getParent()}"
    return result

def gather_explain(query_plan, node):
    # https://www.postgresql.org/docs/10/how-parallel-query-works.html
    result =f"Children executed in parellel (see graph) to get {node.getParent()}"
    return result
    
    
def explainer_map(query_plan, node):
    node_type = query_plan["Node Type"]
    if node_type == "Aggregate": 
        return aggregate(query_plan, node)
    elif node_type == "Append": 
        return append_explain(query_plan, node)
    elif node_type == "CTE Scan": 
        return cte_explain(query_plan, node)
    elif node_type == "Function Scan": 
        return function_scan_explain(query_plan, node)
    elif node_type == "Group": 
        return group_explain(query_plan, node)
    elif node_type == "Index Scan": 
        return index_scan_explain(query_plan, node)
    elif node_type == "Index Only Scan": 
        return index_only_scan_explain(query_plan, node)
    elif node_type == "Limit": 
        return limit_explain(query_plan, node)
    elif node_type == "Materialize": 
        return materialize_explain(query_plan, node)
    elif node_type == "Unique": 
        return unique_explain(query_plan, node)
    elif node_type == "SetOp": 
        return setop_explain(query_plan, node)
    elif node_type == "Test": 
        return test_explain(query_plan, node)
    elif node_type == "Sort": 
        return sort_explain(query_plan, node)
    elif node_type == "Hash": 
        return hash_explain(query_plan, node)
    elif node_type == "Hash Join": 
        return hash_join_explain(query_plan, node)
    elif node_type == "Nested Loop": 
        return nested_loop_explain(query_plan, node)
    elif node_type == "Seq Scan": 
        return seq_scan_explain(query_plan, node)
    elif node_type == "Values Scan": 
        return values_scan_explain(query_plan, node)
    elif node_type == "Subquery Scan": 
        return subquery_scan_explain(query_plan, node)
    elif node_type == "Merge Join": 
        return merge_join_explain(query_plan, node)
    elif node_type == "Gather": 
        return gather_explain(query_plan, node)
    elif node_type == "Memoize": 
        return memoize_explain(query_plan, node)
    elif node_type == "Gather Merge": 
        return gather_merge_explain(query_plan, node)
    else:
        print(node_type)
        # don't have gather, gather merge and memoize
    
    