from nested_mapping import NestedMapping
from nested_mapping.visitor import NestedMappingVisitorDemostrator

def test_nested_mapping_04_visitor():
    dct = dict([('a', 1), ('b', 2), ('c', 3), ('d', dict(e=4)), ('f', dict(g=dict(h=5)))])
    dct['z.z.z'] = 0
    dw = NestedMapping(dct)

    keys0 = (('a',) , ('b',) , ('c',) , ('d', 'e'), ('f', 'g', 'h'), ('z.z.z', ))
    values0 = (1, 2, 3, 4, 5, 0)

    keys = tuple(dw.walkkeys())
    values = tuple(dw.walkvalues())
    assert keys==keys0
    assert values==values0

    class Visitor:
        keys, values = (), ()
        def __call__(self, k, v):
            self.keys+=k,
            self.values+=v,
    v = Visitor()
    dw.visit(v)
    assert v.keys==keys0
    assert v.values==values0

def test_nested_mapping_05_visitor():
    dct = dict([('a', 1), ('b', 2), ('c', 3), ('d', dict(e=4)), ('f', dict(g=dict(h=5)))])
    dct['z.z.z'] = 0
    dw = NestedMapping(dct)

    dw.visit(NestedMappingVisitorDemostrator())
