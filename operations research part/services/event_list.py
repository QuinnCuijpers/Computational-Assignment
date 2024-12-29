import heapq
from models.event import Event
from typing import List


class FutureEventsList:
    # Manages a priority queue of future events in the simulation
    # Events are ordered by their date (chronologically)

    def __init__(self) -> None:
        # Initialize empty list for storing events as a priority queue
        self._heap: List[Event] = []

    def add_event(self, event: Event) -> None:
        # Add a new event to the priority queue
        # Events are automatically sorted by date due to Event's __lt__ method
        heapq.heappush(self._heap, event)

    def pop_event(self) -> Event:
        # Remove and return the earliest event
        # Raises IndexError if queue is empty
        if not self._heap:
            raise IndexError("Pop from an empty heap")
        return heapq.heappop(self._heap)

    def peek_event(self) -> Event:
        # Look at the earliest event without removing it
        # Raises IndexError if queue is empty
        if not self._heap:
            raise IndexError("Peek from an empty heap")
        return self._heap[0]

    def __len__(self) -> int:
        return len(self._heap)

    def __repr__(self) -> str:
        return f"FutureEventsList({self._heap})"
