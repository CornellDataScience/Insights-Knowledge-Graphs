from get_id_vecs import *

def combine_relations(R, thresh):
    """
    R is a (M, N) matrix where M is the number of relations and N is the size of a relation
    Returns a list of K indices and a (K, N) matrix where K is the new number of relations 
    which have been combined based on the cosine similarity threshold
    """
    still_combining = True
    combined = np.copy(R)
    indices = list(range(len(R)))
    newindices = list(range(len(R)))
    while still_combining:
        still_combining = False
        for i in range(len(combined)):
            for j in range(len(combined)-1,i,-1):
                cos_sim = np.dot(combined[i,:], combined[j,:]) / (np.linalg.norm(combined[i,:]) * np.linalg.norm(combined[j,:]))
                if cos_sim > thresh:
                    still_combining = True
                    combined = np.delete(combined, j, 0)
                    newindices[indices.pop(j)] = i
    return newindices, combined

def reduce_relations(ridfile, rvecfile, reducefile, thresh):
    rids = get_ids(ridfile)
    rvecs = get_vectors(rvecfile)
    newids, rvecs = combine_relations(rvecs, thresh)
    with open(reducefile, "w") as outfile:
      for i in newids:
        outfile.write("%s\t%s\n" %(rids[i], i))
