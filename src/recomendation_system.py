from joblib import load
import pandas as pd
import numpy as np
import surprise


modelo = load('modelo_algo_cosine.joblib')