import random
import threading
import math

def randomized_user_list(
        lists,
        min_number,
        batch_size=100,
        iters_per_batch=50,
        iters_per_search=8,
        parallel_threads=4):
    """
    This method searches "lists" of profiles for the shortest list of profiles,
    so that each game will be represented for at least "min_number" of gamers.
    :param lists: list of lists of profiles per game.
    :param min_number: min number of gamers representing each game.
    :param batch_size: size of sequential searches
    :param iters_per_batch: 
    :param iters_per_search: how many searches we'd like to perform. will be rounded up to multiple of threads.
    :param parallel_threads: in how many parallel threads
    :return: shortest achieved list of users
    """

    # SUBMETHODS:

    def random_from_list(
            list,
            already_saved,
            number):
        """
        This method returns up to "number" of items from "list" that are not in "already_taken".
        First, for each item from "list" that appears on "already_saved" reduce "number" by 1 and
        remove that item from "list". (If at any time "number" < 0, return empty list.)
        Then return remaining "number" of random items from the "list".
        :param list: list of profiles
        :param already_saved: already saved profiles
        :param number: minimum profiles per game
        :return: list of new profiles.
        """
        if len(list) < number:
            for i in list[:]:
                if i in already_saved:
                    list.remove(i)
            return list
        random.shuffle(list)
        for i in list[:]:
            if i in already_saved:
                list.remove(i)
                number -= 1
                if number <= 0:
                    return []
        return list[:number + 1]

    def random_from_lists_bestof(
            lists,
            already_saved,
            number,
            iter=50):
        """
        This method, in "iter" iterations, tries to perform method "random_from_list" for each list
        in "lists", in such a way that the returned list is the shortest.
        :param lists: list of lists of profiles
        :param already_saved: profiles we've already saved
        :param number: number of profiles minimum per game
        :param iter: number of iterations (the shorter the returned list, the better)
        :return: list of profiles.
        """
        return_list = []

        # treat lists shorter than "number" differently to save time
        for list in lists[:]:
            if len(list) <= number:
                for i in list:
                    return_list.append(i)
                lists.remove(list)
        return_list = list(set(return_list))
        for i in return_list[:]:
            if i in already_saved:
                return_list.remove(i)

        # fill saved list in such a way that new lists HAVE to be shorter than that
        candidate = [i for i in range(lists * number)]

        for i in range(iter):
            # make random searches for each list
            # at the end check the length of total returned list
            # if that's shorter than length of previously returned list, keep it
            new_candidate = []
            random.shuffle(lists)
            for list in lists:
                new = random_from_list(list, already_saved + return_list + new_candidate, number)
                new_candidate += new[:]
            if len(new_candidate) < len(candidate):
                candidate = new_candidate[:]
            print('iteration %d, returned %d new items.' % (i, len(new_candidate)))

        print('after %d iterations, returned %d new items' % (iter, len(candidate)))
        return_list += candidate
        return return_list

    # SUBMETHODS END

    lists = ordered(lists, key=len)

    saved_profiles = []
    # first, take care of lists shorter than min_number
    for list in lists[:]:
        if len(list) <= min_number:
            saved_profiles += list
            lists.remove(list)
    saved_profiles = list(set(saved_profiles))
    print('initialized with %d must-have profiles' % (len(saved_profiles)))

    candidate = [i for i in range(len(lists)*min_number)]

    def search_thread():
        global iters_per_search
        global parallel_threads
        global candidate

        def search():
            global lists
            lists = lists[:]
            global min_number
            global batch_size
            global iters_per_batch

            loop = True
            return_list = []
            while loop:
                batch = []
                # create batch
                for i in range(batch_size):
                    try:
                        batch.append(lists[0])
                        del lists[0]
                    except IndexError:  # list is empty now, break loop
                        loop = False
                # perform on batch
                new = random_from_lists_bestof(batch, saved_profiles + return_list,
                                               min_number, iters_per_batch)
                return_list += new[:]
            return return_list

        for i in range(math.ceil(iters_per_search/math.max(parallel_threads, 1))):
            new_candidate = search()
            if len(new_candidate) < len(candidate):
                candidate = new_candidate[:]

    threads = []
    for i in range(parallel_threads):
        t = threading.Thread(target=search_thread())
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    saved_profiles += candidate
    return saved_profiles



