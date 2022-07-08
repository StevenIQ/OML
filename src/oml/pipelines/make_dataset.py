# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv
import pandas as pd

# @click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())

def main():
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    logger.info('making final data set from raw data')
    X = pd.read_csv("../../data/raw/NHANESI_X.csv")
    Y = pd.read_csv("../../data/raw/NHANESI_Y.csv")
    df = pd.merge(X, Y, on=['Unnamed: 0']).rename(columns={'Unnamed: 0': "ID"})
    df['date'] = pd.date_range(start='1/1/2019', periods=len(df), freq='H')
    newdf = pd.to_datetime(df['date']).dt.normalize()
    df['date'] = newdf

    df.to_csv("../../data/processed/NHANESI_with_temporal.csv", index=False)




if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
