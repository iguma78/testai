# API Reference

## `result_ai_cm`

The main context manager class for monitoring OpenAI API calls.

### Constructor

```python
result_ai_cm(task_name: str, **kwargs)
```

**Parameters:**
- `task_name`: A string identifier for the current task
- `**kwargs`: Additional keyword arguments to be stored with the API call data

### Methods

#### `__enter__`

```python
__enter__() -> result_ai_cm
```

Enter the context manager and patch the OpenAI API. Returns the context manager instance.

#### `__exit__`

```python
__exit__(exc_type, exc_val, exc_tb) -> None
```

Exit the context manager and restore the original OpenAI API function.

**Parameters:**
- `exc_type`: Exception type if an exception was raised
- `exc_val`: Exception value if an exception was raised
- `exc_tb`: Exception traceback if an exception was raised

## `add_to_queue`

Function to add data to the request queue for processing.

```python
add_to_queue(data: Dict[str, Any]) -> None
```

**Parameters:**
- `data`: The data to add to the queue

## Global Variables

### `request_queue`

A queue for batching requests to the API endpoint.

### `worker_thread`

A background thread that processes the queue and sends batched requests to the API endpoint.
