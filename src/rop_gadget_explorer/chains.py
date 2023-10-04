from abc import abstractclassmethod
from .gadgets import *

class Chain:
    STRATEGIES = ()
    
    def __init__(self, gadgets, **kwargs) -> None:
        self.gadgets = list(gadgets)
        self.attributes = kwargs
    
    def __str__(self) -> str:
        addresses = (hex(gadget.address) for gadget in self.gadgets)
        instructions = (' ; '.join(gadget.instructions) for gadget in self.gadgets)
        return f"({', '.join(addresses)}) # {' | '.join(instructions)}"
    
    #@abstractclassmethod
    #def build(cls, in_file, stack = [], **kwargs):
    #    for strategy in cls.STRATEGIES:
    #        stack.append(strategy)
    #        results = strategy.build(in_file, stack, **kwargs)
    #        yield from results
    #        stack.pop()


class Strategy:

    def _build(self, in_file, stack=[], **kwargs):
        raise NotImplementedError()
    
    def build(self, in_file, stack=[], **kwargs):
        stack_entry = (self, kwargs)
        print(stack)
        print(stack_entry)
        print()
        if stack_entry not in stack:
            stack.append(stack_entry)
            yield from self._build(in_file, stack, **kwargs)
            stack.pop()
        else:
            return None


class SingletonStrategy(Strategy):
    def __init__(self, gadget) -> None:
        super().__init__()
        self.gadget = gadget

    def _build(self, in_file, stack, **kwargs):
        in_file.seek(0) # ensure we read from the start
        for line in in_file:
            res = self.gadget.from_string(line, **kwargs)
            if res:
                yield res


def _update_args(arg_spec, arguments):
        result = arguments.copy()
        for name, spec in arg_spec.items():
            updated_value = spec.format(**arguments)
            result[name] = updated_value
        return result

def _fix_args(candidate, updated_args):
    fixed_args = updated_args.copy()
    for arg in updated_args:
        attr = arg.replace("target", "register") # monkey-patch for divergent nomenclature. TODO: Fix this by refactoring the gadgets!
        attributes = vars(candidate)
        if attr in attributes:
            fixed_args[arg] = attributes[attr]
    return fixed_args


class CompositeStrategy(Strategy):
    def __init__(self, *args) -> None:
        super().__init__()
        self.construction = args
    
    def _build_step(self, in_file, stack, next_step, steps, **kwargs):
        step_cls, args = next_step
        step = step_cls()
        updated_args = _update_args(args, kwargs)
        candidates = step.build(in_file, stack, **updated_args)
        for candidate in candidates:
            next_step = next(steps, None)
            if next_step:
                fixed_args = _fix_args(candidate, updated_args)
                next_step_candiates = self._build_step(in_file, stack, next_step, steps, **fixed_args)
                for nsc in next_step_candiates:
                    result = nsc + [candidate]
                    yield result.copy()
            else:
                yield [candidate]

    def _build(self, in_file, stack, **kwargs):
        steps = reversed(self.construction)
        next_step = next(steps)
        chains = self._build_step(in_file, stack, next_step, steps, **kwargs)
        for chain in chains:
            yield Chain(chain)


class AggregateStrategy(Strategy):

    @classmethod
    def get_strategies(cls):
        raise NotImplementedError()
    
    def _build(self, in_file, stack=[], **kwargs):
        for strategy in self.get_strategies():
            results = strategy.build(in_file, stack, **kwargs)
            yield from results



class SetZeroChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return (
            SingletonStrategy(SetRegisterZeroGadget),
        )


class SubtractionChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return  (
            SingletonStrategy(SubtractGadget),
            CompositeStrategy(
                    (NegateChainFactory, {"target": "{target_a}"}),
                    (AdditionChainFactory, {"target_a": "{target_a}", "target_b": "{target_b}"})
            ),
        )


class NegateChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return  (
            SingletonStrategy(NegateRegisterGadget),
        )


class AdditionChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return  (
            SingletonStrategy(AdditionGadget),
            CompositeStrategy(
                    (NegateChainFactory, {"target": "{target_a}"}),
                    (SubtractionChainFactory, {"target_a": "{target_a}", "target_b": "{target_b}"})
            ),
        )


class MoveChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return  (
            SingletonStrategy(MoveGadget),
            CompositeStrategy(
                    (SetZeroChainFactory, {"target": "{target_b}"}),
                    (AdditionChainFactory, {"target_a": "{target_a}", "target_b": "{target_b}"})
            ),
            #CompositeStrategy(
            #        (ExchangeChainFactory, {"target_a": "{target_a}", "target_b": "{target_b}"}),
            #        (MoveChainFactory, {"target_a": "{target_b}", "target_b": "{target_a}"}),
            #),
    )


class ExchangeChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return  (
            SingletonStrategy(ExchangeRegisterGadget),
        )