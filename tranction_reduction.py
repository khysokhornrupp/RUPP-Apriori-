import imp
from telnetlib import RCP
from typing_extensions import Self
import numpy as np
import typing
import itertools
import numpy_indexed as npi
import pandas as pd
from functools import reduce

from soupsieve import select


class TranctionReduction:
    def __init__(self, itemsets):
        # RC count generation
        self. itemset_reduct, self.rc_values = npi.count(itemsets.values)

    def rc(self, item_np):
        np_hash = {}
        item_rc = []
        for item in item_np:
            key = " ".join(map(str, item))
            if np_hash.get(key):
                np_hash[key] += 1
            else:
                np_hash[key] = 1

        for item in np_hash:
            values = list(map(int,  item.split()))
            values.append(np_hash[item])
            item_rc.append(values)
        return item_rc

    def df_rc(self, item_sets):
        # RC counr and tranction after reduce
        rc_np = np.array(self.rc(item_sets.values))
        df_rc = pd.DataFrame(rc_np)
        columns = list(item_sets.columns)
        columns.append("RC")
        df_rc.set_axis(columns, inplace=True, axis=1)
        RC = df_rc['RC']
        df_rc.drop(['RC'], axis=1, inplace=True)
        self.RC = RC
        self.df_rc = df_rc
        return df_rc, RC

    # Support Count
    # reduce(function, input)
    def support_k_itemst(self, k_itemst):
        s = 0
        for i in range(len(k_itemst)):
            s += reduce(lambda a, b: a & b, k_itemst[i] & self.RC[i])
        return s

    def support_appriori(self, k_itemset, item_sets):
        # get all row which value are equal to 1
        mask = (k_itemset == 1).all(axis=1)
        return len(item_sets[mask]) / len(item_sets)

    def get_frequent_tranc_redu(self, itemesets, min_support, prev_discard):
        L = []
        support_count = []
        new_discard = []
        k = len(prev_discard)
        for i in range(len(itemesets)):
            discard_before = False
            result = itemesets[i]

            # if result in prev_discard than break this loop
            if k > 0:
                for it in prev_discard[k]:
                    if set(it).issubset(set(result)):
                        discard_before = True
                        break

            if not discard_before:
                # print(f'item {mergeKItemIntoOne(item)}')
                count = self.support_k_itemst(self.df_rc[result].values)
                if count >= min_support:
                    L.append(result)
                    support_count.append(count)
                else:
                    new_discard.append(result)
        return L, support_count, new_discard

    def get_frequent_tranc_apiori(self, ck, min_support, prev_discard, item_sets):
        L = []
        support_count = []
        new_discard = []
        k = len(prev_discard)
        for i in range(len(ck)):
            discard_before = False
            result = ck[i]

            # if result in prev_discard than break this loop
            if k > 0:
                for it in prev_discard[k]:
                    if set(it).issubset(set(result)):
                        discard_before = True
                        break

            if not discard_before:
                # print(f'item {mergeKItemIntoOne(item)}')
                count = self.support_appriori(self.df_rc[result], item_sets)
                if count >= min_support:
                    L.append(result)
                    support_count.append(count)
                else:
                    new_discard.append(result)
        return L, support_count, new_discard

    def frequent_item_set_gen(self, minimum_support):
        C = {}
        L = {}
        k_items = []
        Discard = {}
        itemset_size = 1
        Discard.update({itemset_size: []})

        # remove each column who support count are less than min_support for 1 itemsets
        # ---------------------------
        rc_1_itemset = self.df_rc.sum(axis=0)
        # remove all column which sum of row are ness than user defind support threshold
        cut_our_cols = rc_1_itemset.loc[lambda x: x < minimum_support].index
        # cut our every itemset which are sum of each row are less than user defind support
        self.df_rc.drop(labels=cut_our_cols, axis=1, inplace=True)
        # updpate the first item set which are in frequent
        Discard.update({itemset_size: cut_our_cols})

        # Frequent 1 itemsets
        C.update({itemset_size: np.reshape(list(self.df_rc.columns), (-1, 1))})

        support_count = {}
        f, supp, new_discard, = self. get_frequent_tranc_redu(
            C[itemset_size], minimum_support, Discard)

        Discard.update({itemset_size: new_discard})
        L.update({itemset_size: f})
        support_count.update({itemset_size: supp})

        k = itemset_size + 1
        while True:
            try:
                C.update(
                    {
                        k: list(join_step(L[k - 1]))
                    }
                )
                f, supp, new_discard = self.get_frequent_tranc_redu(
                    C[k], minimum_support, Discard)
                L.update({k: f})
                Discard.update({k: new_discard})
                support_count.update({k: supp})
                if(len(L[k]) == 0):
                    break
                k += 1
            except ValueError as err:
                print(f"Hello, there some error with {err}")
                break
        return C, support_count, Discard

    def frequent_item_set_gen_apiori(self, item_sets, minimum_support ):
        C = {}
        L = {}
        Discard = {}
        itemset_size = 1
        Discard.update({itemset_size: []})

        # remove each column who support count are less than min_support for 1 itemsets
        # ---------------------------
        rc_1_itemset = item_sets.sum(axis=0)
        # remove all column which sum of row are ness than user defind support threshold
        cut_our_cols = rc_1_itemset.loc[lambda x: x < minimum_support].index
        # cut our every itemset which are sum of each row are less than user defind support
        item_sets.drop(labels=cut_our_cols, axis=1, inplace=True)
        # updpate the first item set which are in frequent
        Discard.update({itemset_size: cut_our_cols})

        # Frequent 1 itemsets
        C.update({itemset_size: np.reshape(list(item_sets.columns), (-1, 1))})

        support_count = {}
        f, supp, new_discard = self.get_frequent_tranc_apiori(
                    C[itemset_size], minimum_support, Discard, item_sets)

        Discard.update({itemset_size: new_discard})
        L.update({itemset_size: f})
        support_count.update({itemset_size: supp})

        k = itemset_size + 1
        # while True:
        #     try:
        #         C.update(
        #             {
        #                 k: list(join_step(L[k - 1]))
        #             }
        #         )
        #         f, supp, new_discard = self.get_frequent_tranc_apiori(
        #             C[k], minimum_support, Discard, item_sets)
        #         L.update({k: f})
        #         Discard.update({k: new_discard})
        #         support_count.update({k: supp})
        #         if(len(L[k]) == 0):
        #             break
        #         k += 1
        #     except ValueError as err:
        #         print(f"Hello, there some error with {err}")
        #         break
       
        return C, support_count, Discard


def join_step(itemsets: typing.List[tuple]):
    i = 0

    while i < len(itemsets):

        skip = 1

        * itemset_first, itemset_last = itemsets[i]

        tail_items = [itemset_last]
        tail_items_append = tail_items.append

        for j in range(i + 1, len(itemsets)):

            *itemset_n_first, itemset_n_last = itemsets[j]

            if itemset_first == itemset_n_first:  # k - 1, item are identical
                tail_items_append(itemset_n_last)
                skip += 1
            else:
                break

        itemset_first_tuple = tuple(itemset_first)
        for a, b in sorted(itertools.combinations(tail_items, 2)):
            yield list(itemset_first_tuple + (a,) + (b,))

        i += skip


def prune_step(itemsets: typing.Iterable[tuple], possible_itemsets: typing.List[tuple]):
    itemsets = [
        np.unique(subarr) for subarr in itemsets
    ]
    for possible_itemset in possible_itemsets:
        for i in range(len(possible_itemset) - 2):
            removed = possible_itemset[:i] + possible_itemset[i + 1:]
            if (np.array(removed) not in np.array(itemsets)):
                break
            else:
                yield possible_itemset
            yield possible_itemset


def apriori_gen(item_sets):
    posible_extenstion = join_step(item_sets)
    yield from prune_step(item_sets, posible_extenstion)
