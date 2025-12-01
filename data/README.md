# Data Directory

Place your PDF documents in the `pdfs/` subdirectory for indexing.

## Structure
- `pdfs/` - PDF documents to be indexed
- `acl_mapping.json` - Access control list mapping document IDs to authorized user IDs

## ACL Mapping Format
```json
{
  "document_id": ["user1", "user2", "user3"]
}
```

Replace document IDs with the actual hashes generated during ingestion, or set up your own ID scheme.
