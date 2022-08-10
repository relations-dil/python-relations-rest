# relations-rest

API Modeling through REST

Relations overall is designed to be a simple, straight forward, flexible DIL (data interface layer).

Quite different from other DIL's, it has the singular, microservice based purpose to:
- Create models with very little code, independent of backends
- Create CRUD API with a database backend from those models with very little code
- Create microservices to use those same models but with that CRUD API as the backend

Ya, that last one is kinda new I guess and the purpose of this package.

Say we create a service, composed of microservices, which in turn is to be consumed by other services made of microservices.

You should only need to define the model once. Your conceptual structure is the same, to the DB, the API, and anything using that API. You shouldn't have say that structure over and over. You shouldn't have to define CRUD endpoints over and over. That's so boring, tedious, and unnecessary.

Furthermore, the conceptual structure is based not the backend of what you've going to use at that moment of time (scaling matters) but on the relations, how the pieces interact. If you know the structure of the data, that's all you need to interact with the data.

So with Relations, Models and Fields are defined independent of any backend, which instead is set at runtime. So the API will use a DB, everything else will use that API.

This is what allows those same models to use a CRUD API as a backend.

Don't have great docs yet so I've included some of the unittests to show what's possible.

# Example

## define

```python

import relations
import relations_pymysql

# The source is a string, the backend of which is defined at runtime

class SourceModel(relations.Model):
    SOURCE = "RestSource"

class Simple(SourceModel):
    id = int
    name = str

class Plain(SourceModel):
    ID = None # This table has no primary id field
    simple_id = int
    name = str

# This makes Simple a parent of Plain

relations.OneToMany(Simple, Plain)

class Meta(SourceModel):
    id = int
    name = str
    flag = bool
    spend = float
    people = set # JSON storage
    stuff = list # JSON stroage
    things = dict, {"extract": "for__0____1"} # Extracts things["for"][0][-1] as a virtual column
    push = str, {"inject": "stuff___1__relations.io____1"} # Injects this value into stuff[-1]["relations.io"]["1"]

def subnet_attr(values, value):

    values["address"] = str(value)
    min_ip = value[0]
    max_ip = value[-1]
    values["min_address"] = str(min_ip)
    values["min_value"] = int(min_ip)
    values["max_address"] = str(max_ip)
    values["max_value"] = int(max_ip)

class Net(SourceModel):

    id = int
    ip = ipaddress.IPv4Address, { # The field type is that of a class, with the storage being JSON
        "attr": {
            "compressed": "address", # Storge compressed attr as address key in JSON
            "__int__": "value"       # Storge int() as value key in JSON
        },
        "init": "address",           # Initilize with address from JSON
        "titles": "address",         # Use address from JSON as the how to list this field
        "extract": {
            "address": str,          # Extract address as virtual column
            "value": int             # Extra value as virtual column
        }
    }
    subnet = ipaddress.IPv4Network, {
        "attr": subnet_attr,
        "init": "address",
        "titles": "address"
    }

    TITLES = "ip__address" # When listing, use ip["address"] as display value
    INDEX = "ip__value"    # Create an index on the virtual column ip __value

class Unit(SourceModel):
    id = int
    name = str, {"format": "fancy"}

class Test(SourceModel):
    id = int
    unit_id = int
    name = str, {"format": "shmancy"}

class Case(SourceModel):
    id = int
    test_id = int
    name = str

relations.OneToMany(Unit, Test)
relations.OneToOne(Test, Case)

# With this statement, all the above models now how this API endpoint as the backend

self.source = relations_pymysql.Source("RestSource", "http://localhost")
```

## create

```python
simple = Simple("sure")
simple.plain.add("fine")

simple.create()

self.assertEqual(simple.id, 1)
self.assertEqual(simple._action, "update")
self.assertEqual(simple._record._action, "update")
self.assertEqual(simple.plain[0].simple_id, 1)
self.assertEqual(simple.plain._action, "update")
self.assertEqual(simple.plain[0]._record._action, "update")

simples = Simple.bulk().add("ya").create()

self.assertEqual(simples._models, [])

yep = Meta("yep", True, 3.50, {"tom", "mary"}, [1, None], {"a": 1, "for": [{"1": "yep"}]}, "sure").create()
self.assertTrue(Meta.one(yep.id).flag)

nope = Meta("nope", False).create()
self.assertFalse(Meta.one(nope.id).flag)

# This checks teh mock source of the API the models are accessing

self.assertEqual(self.resource.ids, {
    "simple": 2,
    "plain": 1,
    "meta": 2
})

self.assertEqual(self.resource.data, {
    "simple": {
        1: {
            "id": 1,
            "name": "sure"
        },
        2: {
            "id": 2,
            "name": "ya"
        }
    },
    "plain": {
        1: {
            "simple_id": 1,
            "name": "fine"
        }
    },
    "meta": {
        1: {
            "id": 1,
            "name": "yep",
            "flag": True,
            "spend": 3.50,
            "people": ["mary", "tom"],
            "stuff": [1, {"relations.io": {"1": "sure"}}],
            "things": {"a": 1, "for": [{"1": "yep"}]},
            "things__for__0____1": "yep"
        },
        2: {
            "id": 2,
            "name": "nope",
            "flag": False,
            "spend": None,
            "people": [],
            "stuff": [{"relations.io": {"1": None}}],
            "things": {},
            "things__for__0____1": None
        }
    }
})
```

## retrieve

```python
Unit([["people"], ["stuff"]]).create()

models = Unit.one(name__in=["people", "stuff"])
self.assertRaisesRegex(relations.ModelError, "unit: more than one retrieved", models.retrieve)

model = Unit.one(name="things")
self.assertRaisesRegex(relations.ModelError, "unit: none retrieved", model.retrieve)

self.assertIsNone(model.retrieve(False))

unit = Unit.one(name="people")

self.assertEqual(unit.id, 1)
self.assertEqual(unit._action, "update")
self.assertEqual(unit._record._action, "update")

unit = Unit.one(like="p")

self.assertEqual(unit.id, 1)
self.assertEqual(unit._action, "update")
self.assertEqual(unit._record._action, "update")

unit.test.add("things")[0].case.add("persons")
unit.update()

Meta("yep", True, 1.1, {"tom"}, [1, None], {"a": 1}).create()
model = Meta.one(name="yep")

self.assertEqual(model.flag, True)
self.assertEqual(model.spend, 1.1)
self.assertEqual(model.people, {"tom"})
self.assertEqual(model.stuff, [1, {"relations.io": {"1": None}}])
self.assertEqual(model.things, {"a": 1})

self.assertEqual(Unit.many().name, ["people", "stuff"])
self.assertEqual(Unit.many().sort("-name").name, ["stuff", "people"])
self.assertEqual(Unit.many().sort("-name").limit(1, 1).name, ["people"])
self.assertEqual(Unit.many().sort("-name").limit(0).name, [])
self.assertEqual(Unit.many(name="people").limit(1).name, ["people"])

Meta("dive", people={"tom", "mary"}, stuff=[1, 2, 3, None], things={"a": {"b": [1, 2], "c": "sure"}, "4": 5, "for": [{"1": "yep"}]}).create()

model = Meta.many(people={"tom", "mary"})
self.assertEqual(model[0].name, "dive")

model = Meta.many(stuff=[1, 2, 3, {"relations.io": {"1": None}}])
self.assertEqual(model[0].name, "dive")

model = Meta.many(things={"a": {"b": [1, 2], "c": "sure"}, "4": 5, "for": [{"1": "yep"}]})
self.assertEqual(model[0].name, "dive")

model = Meta.many(stuff__1=2)
self.assertEqual(model[0].name, "dive")

model = Meta.many(things__a__b__0=1)
self.assertEqual(model[0].name, "dive")

model = Meta.many(things__a__c__like="su")
self.assertEqual(model[0].name, "dive")

model = Meta.many(things__a__d__null=True)
self.assertEqual(model[0].name, "dive")

model = Meta.many(things____4=5)
self.assertEqual(model[0].name, "dive")

model = Meta.many(things__a__b__0__gt=1)
self.assertEqual(len(model), 0)

model = Meta.many(things__a__c__notlike="su")
self.assertEqual(len(model), 0)

model = Meta.many(things__a__d__null=False)
self.assertEqual(len(model), 0)

model = Meta.many(things___4=6)
self.assertEqual(len(model), 0)

model = Meta.many(things__a__b__has=1)
self.assertEqual(len(model), 1)

model = Meta.many(things__a__b__has=3)
self.assertEqual(len(model), 0)

model = Meta.many(things__a__b__any=[1, 3])
self.assertEqual(len(model), 1)

model = Meta.many(things__a__b__any=[4, 3])
self.assertEqual(len(model), 0)

model = Meta.many(things__a__b__all=[2, 1])
self.assertEqual(len(model), 1)

model = Meta.many(things__a__b__all=[3, 2, 1])
self.assertEqual(len(model), 0)

model = Meta.many(people__has="mary")
self.assertEqual(len(model), 1)

model = Meta.many(people__has="dick")
self.assertEqual(len(model), 0)

model = Meta.many(people__any=["mary", "dick"])
self.assertEqual(len(model), 1)

model = Meta.many(people__any=["harry", "dick"])
self.assertEqual(len(model), 0)

model = Meta.many(people__all=["mary", "tom"])
self.assertEqual(len(model), 1)

model = Meta.many(people__all=["tom", "dick", "mary"])
self.assertEqual(len(model), 0)

Net(ip="1.2.3.4", subnet="1.2.3.0/24").create()
Net().create()

model = Net.many(like='1.2.3.')
self.assertEqual(model[0].ip.compressed, "1.2.3.4")

model = Net.many(ip__address__like='1.2.3.')
self.assertEqual(model[0].ip.compressed, "1.2.3.4")

model = Net.many(ip__value__gt=int(ipaddress.IPv4Address('1.2.3.0')))
self.assertEqual(model[0].ip.compressed, "1.2.3.4")

model = Net.many(subnet__address__like='1.2.3.')
self.assertEqual(model[0].ip.compressed, "1.2.3.4")

model = Net.many(subnet__min_value=int(ipaddress.IPv4Address('1.2.3.0')))
self.assertEqual(model[0].ip.compressed, "1.2.3.4")

model = Net.many(ip__address__notlike='1.2.3.')
self.assertEqual(len(model), 0)

model = Net.many(ip__value__lt=int(ipaddress.IPv4Address('1.2.3.0')))
self.assertEqual(len(model), 0)

model = Net.many(subnet__address__notlike='1.2.3.')
self.assertEqual(len(model), 0)

model = Net.many(subnet__max_value=int(ipaddress.IPv4Address('1.2.3.0')))
self.assertEqual(len(model), 0)
```

## update

```python
Unit([["people"], ["stuff"]]).create()

unit = Unit.many(id=2).set(name="things")

self.assertEqual(unit.update(), 1)

unit = Unit.one(2)

unit.name = "thing"
unit.test.add("moar")

self.assertEqual(unit.update(), 1)
self.assertEqual(unit.name, "thing")
self.assertEqual(unit.test[0].id, 1)
self.assertEqual(unit.test[0].name, "moar")

plain = Plain.one()
self.assertRaisesRegex(relations.ModelError, "plain: nothing to update from", plain.update)

net = Net(ip="1.2.3.4", subnet="1.2.3.0/24").create()

Net.one(net.id).set(ip="5.6.7.8").update()
self.assertEqual(Net.one(net.id).ip.compressed, "5.6.7.8")

meta = Meta("dive", people={"tom", "mary"}, stuff=[1, 2, 3, None], things={"a": {"b": [1, 2], "c": "sure"}, "4": 5, "for": [{"1": "yep"}]}).create()

meta.things["a"]["b"][0] = 3
self.assertEqual(meta.things__a__b__0, 3)

meta.update()

meta = Meta.one(meta.id)

self.assertEqual(meta.things__a__b__0, 3)
```

## delete

```python
unit = Unit("people")
unit.test.add("stuff").add("things")
unit.create()

self.assertEqual(Test.one(id=2).delete(), 1)
self.assertEqual(len(Test.many()), 1)

self.assertEqual(Unit.one(1).test.delete(), 1)
self.assertEqual(Unit.one(1).retrieve().delete(), 1)
self.assertEqual(len(Unit.many()), 0)
self.assertEqual(len(Test.many()), 0)

plain = Plain(0, "nope").create()
self.assertRaisesRegex(relations.ModelError, "plain: nothing to delete from", plain.delete)
```
