//! MemoryBackend trait for all storage backends.

use silas_core::{SilasError, RetrievalResult};
use serde_json::Value;

pub trait MemoryBackend: Send + Sync {
    fn backend_id(&self) -> &str;
    fn store(
        &self,
        content: &str,
        source: &str,
        metadata: Option<&Value>,
    ) -> Result<String, SilasError>;
    fn retrieve(
        &self,
        query: &str,
        top_k: usize,
    ) -> Result<Vec<RetrievalResult>, SilasError>;
    fn delete(&self, doc_id: &str) -> Result<bool, SilasError>;
    fn clear(&self) -> Result<(), SilasError>;
    fn count(&self) -> Result<usize, SilasError>;
}
