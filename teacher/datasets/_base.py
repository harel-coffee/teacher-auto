"""
This module gathers the different datasets used to run the experiments, as well
as a function to take a new generic dataset and return it in a format understandable
by the library
"""

# =============================================================================
# Imports
# =============================================================================

# Standard
from os.path import dirname

# Third party
import pandas as pd
import numpy as np

# Local application
from teacher.utils import recognize_features_type, set_discrete_continuous, label_encode


# =============================================================================
# Constants
# =============================================================================

MODULE_PATH = dirname(__file__)


# =============================================================================
# Functions
# =============================================================================

def generate_dataset(df, columns, class_name, discrete, name):
    """Generate the dataset suitable for LORE usage

    Parameters
    ----------
    df : pandas.core.frame.DataFrame
        Pandas DataFrame with the original data to prepare
    columns : list
        List of the columns used in the dataset
    class_name : str
        Name of the class column
    discrete : list
        List with all the columns to be considered to have discrete values
    name : str
        Name of the dataset

    Returns
    -------
    dataset : dict
        Dataset as a dictionary with the following elements:
            name : Name of the dataset
            df : Pandas DataFrame with the original data
            columns : list of the columns of the DataFrame
            class_name : name of the class variable
            possible_outcomes : list with all the values of the class column
            type_features : dict with all the variables grouped by type
            features_type : dict with the type of each feature
            discrete : list with all the columns to be considered to have discrete values
            continuous : list with all the columns to be considered to have continuous values
            idx_features : dict with the column name of each column once arranged in a NumPy array
            label_encoder : label encoder for the discrete values
            X : NumPy array with all the columns except for the class
            y : NumPy array with the class column
    """
    possible_outcomes = list(df[class_name].unique())

    type_features, features_type = recognize_features_type(df, class_name)
    discrete, continuous = set_discrete_continuous(columns, type_features, class_name, discrete, continuous=None)

    columns_tmp = list(columns)
    columns_tmp.remove(class_name)
    idx_features = {i: col for i, col in enumerate(columns_tmp)}

    # Dataset Preparation for Scikit Alorithms
    df_le, label_encoder = label_encode(df, discrete)
    X = df_le.loc[:, df_le.columns != class_name].values
    y = df_le[class_name].values

    dataset = {
        'name': name,
        'df': df,
        'columns': list(columns),
        'class_name': class_name,
        'possible_outcomes': possible_outcomes,
        'type_features': type_features,
        'features_type': features_type,
        'discrete': discrete,
        'continuous': continuous,
        'idx_features': idx_features,
        'label_encoder': label_encoder,
        'X': X,
        'y': y,
    }

    return dataset


def load_german():
    """
    Load and return the german credit dataset.

    Returns
    -------
    dataset : dict
    """

    # Read Dataset
    df = pd.read_csv(MODULE_PATH + '/data/german_credit.csv', delimiter=',')

    # Features Categorization
    columns = df.columns
    class_name = 'default'

    discrete = ['installment_as_income_perc', 'present_res_since', 'credits_this_bank', 'people_under_maintenance']

    return generate_dataset(df, columns, class_name, discrete, 'german_credit')


def load_adult():
    """
    Load and return the adult dataset.

    Returns
    -------
    dataset : dict
    """

    # Read Dataset
    df = pd.read_csv(MODULE_PATH + '/data/adult.csv', delimiter=',', skipinitialspace=True)

    # Remove useless columns
    del df['fnlwgt']
    del df['education-num']

    # Remove Missing Values
    for col in df.columns:
        df[col].replace('?', df[col].value_counts().index[0], inplace=True)

    # Features Categorization
    columns = df.columns.tolist()
    columns = columns[-1:] + columns[:-1]
    df = df[columns]
    class_name = 'class'

    discrete = []
    return generate_dataset(df, columns, class_name, discrete, 'adult')


def load_compas():
    """
    Load and return the COMPAS scores dataset.

    Returns
    -------
    dataset : dict
    """
    # Read Dataset
    df = pd.read_csv(MODULE_PATH + '/data/compas-scores-two-years.csv', delimiter=',', skipinitialspace=True)

    columns = ['age', 'age_cat', 'sex', 'race', 'priors_count', 'days_b_screening_arrest', 'c_jail_in', 'c_jail_out',
               'c_charge_degree', 'is_recid', 'is_violent_recid', 'two_year_recid', 'decile_score', 'score_text']

    df = df[columns]

    df['days_b_screening_arrest'] = np.abs(df['days_b_screening_arrest'])

    df['c_jail_out'] = pd.to_datetime(df['c_jail_out'])
    df['c_jail_in'] = pd.to_datetime(df['c_jail_in'])
    df['length_of_stay'] = (df['c_jail_out'] - df['c_jail_in']).dt.days
    df['length_of_stay'] = np.abs(df['length_of_stay'])

    df['length_of_stay'].fillna(df['length_of_stay'].value_counts().index[0], inplace=True)
    df['days_b_screening_arrest'].fillna(df['days_b_screening_arrest'].value_counts().index[0], inplace=True)

    df['length_of_stay'] = df['length_of_stay'].astype(int)
    df['days_b_screening_arrest'] = df['days_b_screening_arrest'].astype(int)

    def get_class(x):
        if x < 7:
            return 'Medium-Low'
        else:
            return 'High'

    df['class'] = df['decile_score'].apply(get_class)

    del df['c_jail_in']
    del df['c_jail_out']
    del df['decile_score']
    del df['score_text']

    columns = df.columns.tolist()
    columns = columns[-1:] + columns[:-1]
    df = df[columns]
    class_name = 'class'
    discrete = ['is_recid', 'is_violent_recid', 'two_year_recid']

    return generate_dataset(df, columns, class_name, discrete, 'compas-scores-two-years')


def load_heloc():
    """
    Load and return the HELOC dataset.

    Returns
    -------
    dataset : dict
    """
    # Read Dataset
    df = pd.read_csv(MODULE_PATH + '/data/heloc_dataset_v1.csv', delimiter=',')

    # Features Categorization
    columns = df.columns
    class_name = 'RiskPerformance'

    discrete = []
    return generate_dataset(df, columns, class_name, discrete, 'heloc_dataset_v1')


def load_beer():
    """
    Load and return the beer dataset.

    Returns
    -------
    dataset : dict
    """
    # Read Dataset
    df = pd.read_csv(MODULE_PATH + '/data/beer.csv', delimiter=',')

    # Features Categorization
    class_name = 'beer_style'
    df_cols = list(df.columns)
    df_cols.remove(class_name)
    new_cols = [class_name] + df_cols
    df = df[new_cols]

    discrete = []
    columns = df.columns
    return generate_dataset(df, columns, class_name, discrete, 'beer')


def load_pima():
    """
    Load and return the pima indians dataset.

    Returns
    -------
    dataset : dict
    """
    # Read Dataset
    df = pd.read_csv(MODULE_PATH + '/data/pima-indians-diabetes.csv', delimiter=',')

    # Features Categorization
    class_name = 'Class'
    df_cols = list(df.columns)
    df_cols.remove(class_name)
    new_cols = [class_name] + df_cols
    df = df[new_cols]

    discrete = []
    columns = df.columns
    return generate_dataset(df, columns, class_name, discrete, 'pima')


def load_breast():
    """
    Load and return the breast cancer dataset.

    Returns
    -------
    dataset : dict
    """
    # Read Dataset
    df = pd.read_csv(MODULE_PATH + '/data/breast.csv', delimiter=',')
    del df['id']

    # Features Categorization
    columns = df.columns
    class_name = 'diagnosis'

    discrete = []
    return generate_dataset(df, columns, class_name, discrete, 'breast')
