# Requirements
- Keep it VERY simple
- Need test, docs, instruction
- 2 POST endpoints API
  - 1 to insert or append (server side logic)
  - 1 to get percentile by choice
- Interact with data which includes 2 fields: id (numeric) & values (array of values)
- No database or connection
- Focus on high performance and resiliency
- Reasoning about high-availability and scalability

# Requirement Analysis
## Ambiguous Requirements
- According to the requirements, `id` is numeric and `values` is array of values. ID is not likely to be "numeric" (which has floating point and negative numbers) and "array of values" doesn't imply data type
- Unsure about how the API is going to be used, at which rate

## Decision Made
- `id` will only can be unsigned integer
- `values` will only be array of float
- No database or external service -> Must be local storage
- Key-value, storing array of float -> HDF5 will be used in this case
- Document and instruction needed -> FastAPI for automated API document
- Serve high volume of requests -> ASGI to handle concurrent requests
- Calculating percentile requires a sorted array, but since there's a risk in racing condition, the sorting will be handled in query endpoint.

# Availability and scalability
- HDF5 has good I/O performance, can be compressed
- HDF5 allows us to quickly grab a dataset of choice without loading the whole file
- FastAPI is a production-ready, complete framework which can cut out a lot of work, including type validation, documentation...
- FastAPI uses ASGI, which allow us to serve concurrent requests at ease
- Can deploy to serverless services, and FastAPI has extremely short cold boot compares to other frameworks
- Merge sort is used for better handling at large dataset cases (O(nlogn))
- Numpy Arrays are used instead of Lists for less memory consuming and faster performance

# How to Use
Please make sure you have docker working in your machine.
1. Clone this repo
2. Run `docker build -t pool-api .`
3. Run `docker run -p 8000:8000 pool-api`
4. Check automated documentation generated by FastAPI via `http://127.0.0.1/redoc` or `http://127.0.0.1/docs`

