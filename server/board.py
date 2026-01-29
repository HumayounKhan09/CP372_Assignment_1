from queue import Queue

# you can confidently use this Queue for concurrency
print(Queue().mutex)  # mutex is a lock (hover over it)
# Queue uses the lock internally
