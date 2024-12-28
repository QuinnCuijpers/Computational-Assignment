import heapq
from event import Event
from typing import List


class FutureEventsList:
    _heap: List[Event]

    def __init__(self):
        self._heap = []

    def add_event(self, event: Event):
        heapq.heappush(self._heap, event)

    def pop_event(self) -> Event:
        # Pop the event with the earliest time if the heap is not empty
        if self._heap:
            return heapq.heappop(self._heap)
        else:
            raise IndexError("Pop from an empty heap")

    def peek_event(self) -> Event | None:
        # Peek at the event with the earliest time without removing it
        if self._heap:
            return self._heap[0]
        else:
            return None

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"EventHeap({self._heap})"
