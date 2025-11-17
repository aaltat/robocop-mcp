from invoke import task


@task
def utest(c):
    c.run("pytest --approvaltests-use-reporter='PythonNativeReporter' ./utest")
