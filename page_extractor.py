import re
import pdfplumber
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import math
import spacy
import numpy as np
import statistics
