import heapq
from models.event import Event
from typing import List


class FutureEventsList:
    def __init__(self) -> None:
        self._heap: List[Event] = []

    def add_event(self, event: Event) -> None:
        heapq.heappush(self._heap, event)

    def pop_event(self) -> Event:
        if not self._heap:
            raise IndexError("Pop from an empty heap")
        return heapq.heappop(self._heap)

    def peek_event(self) -> Event:
        if not self._heap:
            raise IndexError("Peek from an empty heap")
        return self._heap[0]

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"FutureEventsList({self._heap})"
