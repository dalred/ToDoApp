# Участник доски

Сущность участник доски, является частью endpoint [**действия с досками**](boards.md)

Где `participants` - перечисление участников доски, их может быть несколько.
```
{
  "participants": [
    {
      "id": 0,
      "role": 1,
      "user": "string",
      "created": "2022-06-26T22:42:46.058Z",
      "updated": "2022-06-26T22:42:46.058Z",
      "board": 0
    }
  ]
}
```