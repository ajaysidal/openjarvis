//! Learning trait definitions.

use silas_core::{SilasError, RoutingContext};
use silas_traces::TraceStore;
use serde_json::Value;
use std::collections::HashMap;

pub trait RouterPolicy: Send + Sync {
    fn select_model(&self, context: &RoutingContext) -> String;
}

pub trait LearningPolicy: Send + Sync {
    fn target(&self) -> &str;
    fn update(
        &self,
        trace_store: &TraceStore,
    ) -> Result<HashMap<String, Value>, SilasError>;
}
