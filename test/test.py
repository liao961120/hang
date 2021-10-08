#%%
from dcctk.corpusReader import PlainTextReader
from dcctk.concordancer import Concordancer
from dcctk.corpus import TextBasedCorpus
from dcctk.embeddings import AnchiBert, semantic_sort

c = Concordancer(PlainTextReader("data/").corpus)

#%%
# c = TextBasedCorpus(PlainTextReader().corpus)
# c.list_files('三國')
# c.get_meta_by_path('03/三國志_蜀書一.txt')
# c.get_text('03/三國志_蜀書一.txt', as_str=True)
texts = c.get_texts('三國志', texts_as_str=False, sents_as_str=True)
texts_str = c.get_texts('三國志', texts_as_str=True, sents_as_str=True)

#%%
cql = '''
"法" "院"
'''.strip()
results = list(c.cql_search(cql, left=10, right=10))
print(len(results))
x = results[0]
#%%
x.get_kwic()
x.get_timestep()

#%%
# Sort Concord
results_sorted = sorted(results, key=lambda x: x.get_timestep())
# results[0].get_timestep()

#%%
emb = AnchiBert()

#%%
base_sent, base_tk = results[17].get_kwic()
print(base_sent)
print(base_tk)
sem_sort_by_tk = semantic_sort(emb, results[:200], base_sent, base_tk)
sem_sort_by_sent = semantic_sort(emb, results[:200], base_sent)

#%%
import gdown


gdown.download('https://drive.google.com/uc?id=1uMlNJzilEhSigIcfjTjPdYOZL9IQfHNK', output="AnchiBERT.zip")

#%%
gdown.extractall("AnchiBERT.zip")

# %%
import cqls
queries = cqls.parse(cql, default_attr=c._cql_default_attr,max_quant=6)

x = c._search_keyword(queries[0][0])
    # for result in c._kwic(keywords=query, left=5, right=5):
    #     results.append(result)
# %%
import math

query = queries[0]

best_search_loc = (0, None, math.inf)
for i, keyword in enumerate(query):
    results = c._search_keyword(keyword)
    num_of_matched = len(results)
    if num_of_matched == 0: 
        pass
    elif num_of_matched < best_search_loc[-1]:
        best_search_loc = (i, results, num_of_matched)
results = best_search_loc[1]


#%%
from dcctk.UtilsConcord import queryMatchToken

keyword_anchor = {
    'length': len(query),
    'seed_idx': best_search_loc[0]
}
keywords = query

matched_results = []
for idx in results:
    # Get all possible matching keywords from corpus
    candidates = c._get_keywords(keyword_anchor, *idx)
    if len(candidates) != len(keywords): 
        continue
    # Check every token in keywords
    matched_num = 0
    for w_k, w_c in zip(keywords, candidates):
        if queryMatchToken(queryTerm=w_k, corpToken=w_c):
            matched_num += 1
    if matched_num == len(keywords):
        first_keyword_idx = idx[2] - keyword_anchor['seed_idx']
        matched_results.append( [idx[0], idx[1], first_keyword_idx] )
# %%