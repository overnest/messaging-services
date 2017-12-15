from click import secho


_TESTS = []


def test(requires=set(), provides=set()):
    def unparameterized_decorator(f):
        def decorated(*args, **kwargs):
            try:
                secho("Running {}...".format(f.__name__), bold=True)
                result = f(*args, **kwargs)
                secho("Passed!", bold=True, fg='green')
                return result
            except Exception as ex:
                secho("Failed!", bold=True, fg='red')
                raise ex

        _TESTS.append((decorated, requires, provides))

        return decorated

    return unparameterized_decorator


def assertion(message, predicate, fatal=True):
    secho("  {}... ".format(message), bold=True, nl=False)

    if predicate():
        secho("yes", bold=True, fg='green')
    elif fatal:
        secho("fail", bold=True, fg='red')
        raise AssertionError
    else:
        secho("no", bold=True, fg='yellow')
