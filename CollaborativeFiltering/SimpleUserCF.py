# -*- coding: utf-8 -*-
"""
@author: Yashodeep
"""

import sys
sys.path.append('CollaborativeFiltering/')    # read this for how to import from diff floders https://stackoverflow.com/a/33773635/11925194
from MovieLens import MovieLens
from surprise import KNNBasic
import heapq
from collections import defaultdict
from operator import itemgetter


 
def runUserColaborativeFiltering(testSubject = "85", k = 14):
    
    # Load our data set and compute the user similarity matrix
    ml = MovieLens()
    data = ml.loadMovieLensLatestSmall()
    # the data is in surprise.dataset.DatasetAutoFolds fromat
    # to get the raw ratings use data.raw_ratings the format is --> userID movieID rating Timestamp
    
    # Trainsets are different from Datasets. You can think of a Dataset as the raw data,
    # and Trainsets as higher-level data where useful methods are defined.
    # build_full_trainset() method will build a trainset object for the entire dataset
    trainSet = data.build_full_trainset()
    
    # Options for similarity calculations
    sim_options = {'name': 'cosine',
                   'user_based': True}
    
    model = KNNBasic(sim_options=sim_options)
    # Fit must be called on a transient only not directly on the raw data
    model.fit(trainSet)
    simsMatrix = model.compute_similarities()
    
    # Get top N similar users to our test subject
    # (Alternate approach would be to select users up to some similarity threshold )
    testUserInnerID = trainSet.to_inner_uid(testSubject)
    similarityRow = simsMatrix[testUserInnerID]
    
    similarUsers = []
    for innerID, score in enumerate(similarityRow):
        if (innerID != testUserInnerID):
            similarUsers.append( (innerID, score) )
    
    kNeighbors = heapq.nlargest(k, similarUsers, key=lambda t: t[1])
    
    # Get the stuff they rated, and add up ratings for each item, weighted by user similarity
    candidates = defaultdict(float)
    for similarUser in kNeighbors:
        innerID = similarUser[0]
        userSimilarityScore = similarUser[1]
        theirRatings = trainSet.ur[innerID]
        for rating in theirRatings:
            candidates[rating[0]] += (rating[1] / 5.0) * userSimilarityScore
        
    # Build a dictionary of stuff the user has already seen
    watched = {}
    for itemID, rating in trainSet.ur[testUserInnerID]:
        watched[itemID] = 1
        
    # Get top-rated items from similar users:
    recommendations = []
    pos = 0
    print("\n\n-------------------<><><><>--------------------")
    for itemID, ratingSum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
        if not itemID in watched:
            movieID = trainSet.to_raw_iid(itemID)
            movieID = float(movieID)
            movieID = int(movieID)
            recommendations.append(int(movieID))
            print(ml.getMovieName(int(movieID)), ratingSum)
            pos += 1
            if (pos > 20):
                break
    print("-------------------<><><><>--------------------")
    # these are the id in the movie lens dataset
    return recommendations


