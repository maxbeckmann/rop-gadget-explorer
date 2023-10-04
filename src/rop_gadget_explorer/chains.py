from abc import abstractclassmethod
from .gadgets import *

class Chain:
    def __init__(self, gadgets, stack, **kwargs) -> None:
        self.gadgets = list(gadgets)
        self.attributes = kwargs
        self.stack = stack
    
    def _get_addresses(self):
        for g in self.gadgets:
            if isinstance(g, Gadget):
                yield g.address
            else:
                yield from g._get_addresses()
    
    def _get_instructions(self):
        for g in self.gadgets:
            if isinstance(g, Gadget):
                yield g.instructions
            else:
                yield from g._get_instructions()

    def __str__(self) -> str:
        addresses = (hex(address) for address in self._get_addresses())
        instructions = (' ; '.join(instructions) for instructions in self._get_instructions())
        return f"({', '.join(addresses)}) # {' | '.join(instructions)}"


class Strategy:

    def _build(self, in_file, stack=[], **kwargs):
        raise NotImplementedError()
    
    def build(self, in_file, stack=[], **kwargs):
        stack_entry = (self, kwargs)
        if stack_entry not in stack:
            stack.append(stack_entry)
            for r in self._build(in_file, stack, **kwargs):
                yield r
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
                attributes = vars(res)
                yield Chain([res], stack, **attributes)


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
        attributes = candidate.attributes
        if attr in attributes:
            fixed_args[arg] = attributes[attr]
    return fixed_args


class CompositeStrategy(Strategy):
    def __init__(self, *args) -> None:
        super().__init__()
        self.construction = args
    
    def _build_step(self, in_file, stack, next_step, steps, **kwargs):
        step, args = next_step
        updated_args = _update_args(args, kwargs)
        candidates = step.build(in_file, stack, **updated_args)
        for candidate in candidates:
            print(candidate)
            print(stack)
            next_step = next(steps, None)
            if next_step:
                fixed_args = _fix_args(candidate, updated_args)
                next_step_candiates = self._build_step(in_file, stack, next_step, steps, **fixed_args)
                for nsc in next_step_candiates:
                    result = nsc + [candidate]
                    yield result.copy()
            else:
                print("reached leaf")
                print()
                print()
                yield [candidate]

    def _build(self, in_file, stack, **kwargs):
        steps = reversed(self.construction)
        next_step = next(steps)
        chains = self._build_step(in_file, stack, next_step, steps, **kwargs)
        for chain in chains:
            yield Chain(chain, stack)


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
            neg_add,
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
            neg_sub,
            neg_sub_neg,
        )


class MoveChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return  (
            SingletonStrategy(MoveGadget),
            zero_add,
            xchg_move,
    )


class ExchangeChainFactory(AggregateStrategy):
    @classmethod
    def get_strategies(cls):
        return  (
            SingletonStrategy(ExchangeRegisterGadget),
        )

move = MoveChainFactory()
xchg = ExchangeChainFactory()
sub = SubtractionChainFactory()
add = AdditionChainFactory()
zero = SetZeroChainFactory()
neg = NegateChainFactory()

neg_sub = CompositeStrategy(
                    (neg, {"target": "{target_a}"}),
                    (sub, {"target_a": "{target_a}", "target_b": "{target_b}"})
            )

neg_sub_neg = CompositeStrategy(
                    (neg, {"target": "{target_b}"}),
                    (sub, {"target_a": "{target_a}", "target_b": "{target}"}),
                    (neg, {"target": "{target_b}"}),
            )

neg_add = CompositeStrategy(
                    (neg, {"target": "{target_a}"}),
                    (add, {"target_a": "{target_a}", "target_b": "{target_b}"})
            )

zero_add = CompositeStrategy(
                    (zero, {"target": "{target_b}"}),
                    (add, {"target_a": "{target_a}", "target_b": "{target_b}"})
            )

xchg_move = CompositeStrategy(
                    (xchg, {"target_a": "{target_a}", "target_b": "{target_b}"}),
                    (move, {"target_a": "{target_b}", "target_b": "{target_a}"}),
            )