import unittest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


class TestAPI(unittest.TestCase):
    def test_insert(self):
        pool_id = 123456
        body = {
           "poolId": pool_id,
           "poolValues": [ 1, 7, 2, 6 ]
        }
        client.delete(f"/delete/{pool_id}")
        r = client.post("/add", json=body)
        resp = r.json()
        self.assertDictEqual(resp, {"status": "inserted"})
        client.delete(f"/delete/{pool_id}")

    def test_append(self):
        pool_id = 123456
        body = {
           "poolId": pool_id,
           "poolValues": [ 1, 7, 2, 6 ]
        }

        client.post("/add", json=body)
        r = client.post("/add", json=body)
        self.assertDictEqual(r.json(), {"status": "appended"})
        client.delete(f"/delete/{pool_id}")

    def test_quantile1(self):
        pool_id = 123
        pool_values = list(range(1000000, 0, -1))
        percentile = 85.5
        add_body = {"poolId": pool_id, "poolValues": pool_values}
        query_body = {"poolId": pool_id, "percentile": percentile}
        client.delete(f"/delete/{pool_id}")
        client.post("/add", json=add_body)
        r = client.post("/query", json=query_body)
        self.assertDictEqual(r.json(), {"quantile": 855000, "total": 1000000})

    def test_quantile2(self):
        pool_id = 123
        pool_values = [-1.2, 32, -52, 100, 282]
        percentile = 80.0
        add_body = {"poolId": pool_id, "poolValues": pool_values}
        query_body = {"poolId": pool_id, "percentile": percentile}
        client.delete(f"/delete/{pool_id}")
        client.post("/add", json=add_body)
        r = client.post("/query", json=query_body)
        self.assertDictEqual(r.json(), {"quantile": 100, "total": 5})

    def test_add_wrong_value_type(self):
        pool_id = 123456
        body1 = {
           "poolId": pool_id,
           "poolValues": [ 1, 7, 2, "string" ]
        }
        client.delete(f"/delete/{pool_id}")
        r = client.post("/add", json=body1)
        self.assertEqual(r.status_code, 422)

    def test_wrong_id_type(self):
        body = {
           "poolId": -10,
           "poolValues": [ 1, 7, 2 ]
        }
        r = client.post("/add", json=body)
        self.assertEqual(r.status_code, 422)

        body = {
           "poolId": "string",
           "poolValues": [ 1, 7, 2 ]
        }
        r = client.post("/add", json=body)
        self.assertEqual(r.status_code, 422)


if __name__ == '__main__':
    unittest.main()

