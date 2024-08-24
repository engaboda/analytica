db.createUser(
    {
      user: "test_db_user",
      pwd:  'test_db_password',
      roles: [{ role: "readWrite", db: "test_db" }]
    }
  )