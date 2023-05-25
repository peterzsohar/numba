import multiprocessing as mp
import traceback
from numba.cuda.testing import unittest, CUDATestCase


def child_test():
    from numba import config, cuda

    # Change the MVC config after importing numba.cuda
    config.CUDA_ENABLE_MINOR_VERSION_COMPATIBILITY = 1

    @cuda.jit
    def f():
        pass

    f[1, 1, 0]()


def child_test_wrapper(result_queue):
    try:
        output = child_test()
        success = True
    # Catch anything raised so it can be propagated
    except: # noqa: E722
        output = traceback.format_exc()
        success = False

    result_queue.put((success, output))


class TestMinorVersionCompatibility(CUDATestCase):
    def test_mvc(self):
        # Run test with Minor Version Compatibility enabled in a child process
        ctx = mp.get_context('spawn')
        result_queue = ctx.Queue()
        proc = ctx.Process(target=child_test_wrapper, args=(result_queue,))
        proc.start()
        proc.join()
        success, output = result_queue.get()

        # Ensure the child process ran to completion before checking its output
        if not success:
            self.fail(output)


if __name__ == '__main__':
    unittest.main()
