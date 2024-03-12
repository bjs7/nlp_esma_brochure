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

def find_toc_page():
    toc_found = False
    for index, page in enumerate(pdf.pages):
        if len(page.extract_words()) >= 5:
            for j in range(10):
                if page.extract_words()[j]['text'].lower() in 'contents':
                    toc_page_nr, toc_page = index, page
                    toc_found = True
                    break
        if toc_found:
            break
    return toc_page_nr, toc_page


class page_extracter:

    def __init__(self, page):
        self.page = page
        self.ToC = []

    def page_slicer(self, scaling=0.075):
        vHeader = (0, 0, self.page.width, self.page.height * scaling)
        vFooter = (0, self.page.height * (1 - scaling), self.page.width, self.page.height)
        vBody = (0, self.page.height * scaling + 1, self.page.width, self.page.height * (1 - scaling) + 1)

        self.cropHeader = self.page.crop(vHeader)
        self.cropFooter = self.page.crop(vFooter)
        self.cropBody = self.page.crop(vBody)

    def head_footer_text(self):

        def slicer(input):
            input = input.extract_text().split(' ')
            lList = []
            for word in input:
                lList.append(''.join(char if char.isdigit() or char.isspace() else '' for char in word.split('\n')[0]))
            return lList
        self.header_text = slicer(self.cropHeader)
        self.footer_text = slicer(self.cropFooter)

    def body_sep_text_title(self):

        # tmp_cropBody = self.cropBody
        x_0 = (1 - 0.005) * self.cropBody.width
        vBox = (x_0, self.page.height * 0.075 + 1, self.cropBody.width, self.page.height * (1 - 0.075) + 1)

        indicator_empty = True
        while indicator_empty:
            if self.cropBody.crop(vBox).extract_text():
                indicator_empty = False
            x_0 = x_0 - self.page.width * 0.005
            vBox = (x_0, self.page.height * 0.075 + 1, self.cropBody.width, self.page.height * (1 - 0.075) + 1)

        tmp_cropBody = self.cropBody.crop(vBox)
        min_height = self.page.height - tmp_cropBody.chars[0]['y1']
        for char in tmp_cropBody.chars:
            if self.page.height - char['y1'] < min_height:
                min_height = self.page.height - char['y1']

        vBox = (0, min_height, self.page.width, self.page.height * (1 - 0.075) + 1)
        self.crop_body_text = self.cropBody.crop(vBox)

        # title
        vBox = (0, self.page.height * 0.075 + 1, self.page.width, min_height - self.page.height * 0.005)
        self.crop_body_title = self.cropBody.crop(vBox)


    def body_cleaner(self, ToC = False):

        if ToC:

            def find_page_number(lText):
                NumberIndex = len(lText) - 1
                char = lText[NumberIndex]
                lNumber = []

                while char.isdigit() and NumberIndex >= 0:
                    lNumber.append(NumberIndex)
                    NumberIndex -= 1
                    char = lText[NumberIndex]

                return lNumber

            def texter(text, j):
                x = text[j]
                # TextIndex = 0
                # char = x[TextIndex]
                i = 0
                while not x[i].isalpha():
                    i += 1
                    if i >= len(x):
                        break

                iEnd = i
                while (x[iEnd:(iEnd + 2)] != ' .' and x[iEnd:(iEnd + 2)] != '..'
                       and x[iEnd:(iEnd + 2)] != ''):
                    iEnd += 1

                textout = x[i:iEnd]

                lNumber = find_page_number(text[j])
                if len(lNumber) == 0:
                    j += 1
                    # lNumber = find_page_number(text[j])
                    txtout, vPage_number, j, = texter(text, j)
                    textout = textout + ' ' + txtout
                    return textout, vPage_number, j
                if len(lNumber) == 1:
                    vPage_number = text[j][lNumber[0]]
                else:
                    vPage_number = text[j][min(lNumber):max(lNumber) + 1]

                # j += 1
                return textout, vPage_number, j

            # recusive af string
            text = self.crop_body_text.extract_text().split('\n')
            j = 0
            while j < len(text):
                tmp_text, vPage_number, j = texter(text, j)
                self.ToC.append([tmp_text, vPage_number])
                j += 1

        else:
            self.totalbodytext = self.cropBody.extract_text()
            listed_page = list(self.totalbodytext)
            vIndicies = []
            observer_bool = False
            for index, text in enumerate(listed_page):
                if text == '"':
                    observer_bool = not observer_bool
                elif not observer_bool and text in '\n':
                    vIndicies.append(index)

                for index in vIndicies:
                    if listed_page[index + 1].isupper() and listed_page[index - 1].isalpha() and listed_page[
                        index + 2].islower():
                        listed_page[index] = '.'
                    else:
                        listed_page[index] = ' '

                output = ''.join(listed_page)
            self.body_text = output.replace('\n', ' ').split('.')
