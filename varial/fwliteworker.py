import ROOT
import itertools
import multiprocessing

import diskio


def _add_results(results_iter):
    res_sums = {}
    for results in results_iter:
        if not res_sums:
            res_sums = dict((r.name, r) for r in results)
        else:
            for res in results:
                res_sum = res_sums[res.name]
                for k, v in res.__dict__.iteritems():
                    if isinstance(v, ROOT.TH1):
                        getattr(res_sum, k).Add(v)
    return res_sums


def _run_workers(args):
    event_handle, workers = args
    for w in workers:
        w.node_setup(event_handle)
    for event in event_handle:
        for w in workers:
            w.node_process_event(event)
    for w in workers:
        w.node_finalize()
    results = list(w.result for w in workers)
    return results


def work(workers, event_handles):
    pool = multiprocessing.Pool()
    results_iter = pool.imap_unordered(
        _run_workers,
        zip(
            event_handles,
            itertools.repeat(workers),
        )
    )
    return _add_results(results_iter)


class FwliteWorker(object):
    def __init__(self, name):
        self.result = diskio.fileservice(name, False)

    def node_setup(self, event_handle):
        pass

    def node_process_event(self, event):
        pass

    def node_finalize(self):
        pass

