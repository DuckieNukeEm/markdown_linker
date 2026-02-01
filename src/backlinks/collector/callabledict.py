from collections.abc import MutableMapping
from typing import Any, Iterator, Mapping, Optional


class CallableDict(MutableMapping):
    """A dictionary-like mapping where stored callables are invoked on access.

    Behavior:
    - By default, accessing an item via `d[key]` will call the stored value if
      it is callable and return the result. Non-callable values are returned
      directly.
    - Use `raw(key)` to retrieve the stored value without calling it.
    - Use `call(key, *args, **kwargs)` to call the stored callable with
      arguments and return its result.
    - Attribute access `d.foo` maps to the same semantics as `d['foo']`.

    The `call_on_get` flag can be set to `False` to disable automatic calling
    on `__getitem__`.
    """

    def __init__(
        self, mapping: Optional[Mapping] = None, *, call_on_get: bool = True
    ):
        self._store = dict(mapping) if mapping is not None else {}
        self.call_on_get = bool(call_on_get)

    # MutableMapping required methods
    def __getitem__(self, key: Any) -> Any:
        try:
            val = self._store[key]
        except KeyError as e:
            raise KeyError(f"Key {key} not found with error: {e}")

        if self.call_on_get and callable(val):
            return val()
        return val

    def __setitem__(self, key: Any, value: Any) -> None:
        self._store[key] = value

    def __delitem__(self, key: Any) -> None:
        del self._store[key]

    def __iter__(self) -> Iterator:
        return iter(self._store)

    def __len__(self) -> int:
        return len(self._store)

    def __contains__(self, key: object) -> bool:  # type: ignore[override]
        return key in self._store

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._store!r}, call_on_get={self.call_on_get})"

    def __str__(self) -> str:
        return str(self._store)

    # Convenience helpers
    def raw(self, key: Any) -> Any:
        """Return the stored value for `key` without calling it."""
        return self._store[key]

    def call(self, key: Any, *args, **kwargs) -> Any:
        """Call the stored callable for `key` with given args/kwargs.

        Raises a TypeError if the stored value is not callable.
        """
        val = self._store[key]
        if not callable(val):
            raise TypeError(f"Value for key {key!r} is not callable")
        return val(*args, **kwargs)

    # Attribute-style access: d.foo -> d['foo'] behavior
    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        # Keep internal attributes as real attributes
        if name in {"_store", "call_on_get"}:
            object.__setattr__(self, name, value)
        elif name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            # Non-internal attribute assignment maps to setting a key
            self[name] = value

    def get(self, key, default_value) -> Any:
        """function to replicate the dict.get"""
        if self[key]:
            return self[key]
        else:
            return default_value


if __name__ == "__main__":
    # Short demo of usage
    def hello():
        return "hello world"

    def add(a, b=0):
        return a + b

    d = CallableDict(
        {
            "greet": hello,
            "const": 42,
            "add": add,
        }
    )

    print("d['greet'] ->", d["greet"])  # calls hello() -> "hello world"
    print("d.raw('greet') ->", d.raw("greet"))  # returns the function object
    print("d.call('add', 2, b=3) ->", d.call("add", 2, b=3))
    print("d['const'] ->", d["const"])  # 42 (non-callable)
    print("attribute access d.greet ->", d.greet)  # also calls hello()
