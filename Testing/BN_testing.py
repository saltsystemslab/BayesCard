from Evaluation.cardinality_estimation import parse_query_single_table
from Evaluation.utils import parse_query
from time import perf_counter
import numpy as np
import pickle

def evaluate_cardinality_single_table(model_path, query_path):
    # load BN
    with open(model_path, 'rb') as f:
        BN = pickle.load(f)
    if BN.infer_machine is None:
        BN.init_inference_method()
    # read all queries
    with open(query_path) as f:
        queries = f.readlines()
    latencies = []
    q_errors = []
    for query_no, query_str in enumerate(queries):
        cardinality_true = int(query_str.split("||")[-1])
        query_str = query_str.split("||")[0]
        print(f"Predicting cardinality for query {query_no}: {query_str}")
        try:
            query = parse_query_single_table(query_str.strip(), BN)
            card_start_t = perf_counter()
            cardinality_predict = BN.query(query)
        except:
            #In the case, that the query itself is invalid
            print("This query is not recognizable")
            continue
        card_end_t = perf_counter()
        latency_ms = (card_end_t - card_start_t) * 1000
        if cardinality_predict == 0 and cardinality_true == 0:
            q_error = 1.0
        elif np.isnan(cardinality_predict) or cardinality_predict == 0:
            cardinality_predict = 1
            q_error = max(cardinality_predict / cardinality_true, cardinality_true / cardinality_predict)
        elif cardinality_true == 0:
            cardinality_true = 1
            q_error = max(cardinality_predict / cardinality_true, cardinality_true / cardinality_predict)
        else:
            q_error = max(cardinality_predict / cardinality_true, cardinality_true / cardinality_predict)
        print(f"latency: {latency_ms} and error: {q_error}")
        latencies.append(latency_ms)
        q_errors.append(q_error)

    print("=====================================================================================")
    for i in [50, 90, 95, 99, 100]:
        print(f"q-error {i}% percentile is {np.percentile(q_errors, i)}")
    print(f"average latency is {np.mean(latencies)} ms")

    return latencies, q_errors


