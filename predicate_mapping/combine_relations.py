from get_id_vecs import *
import matplotlib.pyplot as plt

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

def reduce_relations(ridfile, rvecfile, thresh, reducefile):
    rids = get_ids(ridfile)
    rvecs = get_vectors(rvecfile)
    newids, rvecs = combine_relations(rvecs, thresh)
    with open(reducefile, "w") as outfile:
      for i in range(len(newids)):
        outfile.write("%s\t%s\n" %(rids[newids[i]], i))
    return [rids[i] for i in newids]

def heat_map(idfile, vecfile, thresh, plotfile):
    relations = get_ids(idfile)
    vecs = get_vectors(vecfile)
    sim = np.ones((len(vecs), len(vecs)))
    
    for i in range(len(vecs)):
        for j in range(i, len(vecs)):
            sim[i,j] = sim[j, i] = min(1, np.dot(vecs[i,:], vecs[j,:]) / (thresh * np.linalg.norm(vecs[i,:]) * np.linalg.norm(vecs[j,:])))

    fig, ax = plt.subplots()
    _ = ax.imshow(sim)

    ax.set_xticks(np.arange(len(relations)))
    ax.set_yticks(np.arange(len(relations)))
    ax.set_xticklabels(relations)
    ax.set_yticklabels(relations)

    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")

    ax.set_title("Harvest of local farmers (in tons/year)")
    fig.set_size_inches(10,10)
    plt.savefig(plotfile)

if __name__ == '__main__':
    idfile = './data/relation2id.txt'
    vecfile = './data/relation2vec.csv'
    thresh = 0.22
    reduce_relations(idfile, vecfile, thresh, './data/combined_relations.txt')
    heat_map(idfile, vecfile, thresh, './data/relation_heat_map.png')