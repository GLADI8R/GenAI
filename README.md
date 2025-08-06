

## Setup

- `source venv/bin/activate`
- [MongoDB](https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/)
- 


### MongoDB
- starting: `sudo systemctl start mongod`
- stop: `sudo systemctl stop mongod`
- restart: `sudo systemctl restart mongod`

run `mongosh` to start session


## DB Schema
```
users
|- user_id (int)
|- first_name (string)
|- last_name (string)
|- email (string)
|- gender (string)
|- created_at (string)


orders
|- order_id (int)
|- user_id (int)
|- product_name (string)
|- quantity (int)
|- price (int)
|- order_date (string)
```