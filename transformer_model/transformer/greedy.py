# -*- coding: utf-8 -*-
# date: 2018-12-03 10:36
import torch
from torch.autograd import Variable

from .functional import subsequent_mask


def greedy_decode(model, src, src_mask, max_len, start_symbol):
    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type_as(src.data)
    for i in range(max_len - 1):
        out = model.decode(memory, src_mask, Variable(ys), Variable(subsequent_mask(ys.size(1)).type_as(src.data)))
        prob = model.generator(out[:, -1])
        _, next_word = torch.max(prob, dim=1)
        next_word = next_word.data[0]
        ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=1)
    return ys


def greedy_decode_eval(model, src, src_mask, max_len, start_symbol, end_symbol):
    memory = model.encode(src, src_mask)
    ys = torch.ones(1, 1).fill_(start_symbol).type_as(src.data)
    probs = torch.ones(1,1)
    for i in range(max_len - 1):
        out = model.decode(memory, src_mask, Variable(ys), Variable(subsequent_mask(ys.size(1)).type_as(src.data)))
        prob = model.generator(out[:, -1])
        word_prob, next_word = torch.max(prob, dim=1)
        next_word = next_word.data[0]
        word_prob = word_prob.data[0]
        if next_word == end_symbol:
            return ys, probs
        ys = torch.cat([ys, torch.ones(1, 1).type_as(src.data).fill_(next_word)], dim=1)
        probs = torch.cat([probs, torch.ones(1,1).fill_(word_prob)], dim=1)
    return ys, probs
