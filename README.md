# fin_sentiment: Money Control Stock News Sentiment Tool

## Installing
 Install the dependencies by creating the Conda environment `fin_sentiment` from the given `environment.yml` file and
 activating it.
```bash
conda env create -f environment.yml
conda activate fin_sentiment
```

You could face issues with nltk punkt. If that occurs, please do following in python shell:

```import nltk
nltk.download('punkt')
```

Since we cannot store large pre-trained ML models on GitHub, please download [model](https://drive.google.com/file/d/1Gv-ZiXcfftTtpRGWRVT6yRv1eicJWNJ5/view?usp=sharing) into models folder.

## Getting sentiment
We provide a script to quickly get sentiment predictions. 

From the command line, simply run:
```bash
python process.py --levels <number of nested levels> --output <file name>

```

The above script generates a raw json file aggegrating all the links and a summary html file with sentiment of each article.

Please note that the first time you run this script it attempts to download data files and could take a bit longer to run.
