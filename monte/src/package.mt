# Loaded only to execute tests.

def unittest := pkg.testCollector()

# pkg.readFile("heap.mt")([=> unittest, ...])

def blackjack := pkg.readFile("blackjack.mt")([=> unittest])
def example := pkg.readFile("examples/testing.mt")([=> unittest])
def [=> makeOMeta] := pkg.readFile("ometa.mt")()
def ometaTests := pkg.readFile("test_ometa.mt")([=> makeOMeta, => unittest])
def terml := pkg.readPackage("./terml")()
def testUnicode := pkg.readFile("test_unicode.mt")([=> unittest])

pkg.makeModule(terml | blackjack | example | ometaTests)