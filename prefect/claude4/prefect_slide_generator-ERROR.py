#!/usr/bin/env python3
"""
Prefect Slide Deck Generator
Creates HTML slides about Prefect workflow library with navigation
"""

import os
from pathlib import Path

def create_slide_content():
    """Define all slide content"""
    slides = [
        # Main slides (001-010)
        {
            "number": "001",
            "title": "Introduction to Prefect",
            "content": """
            <h1>🚀 Prefect</h1>
            <h2>Modern Workflow Orchestration</h2>
            <div class="slide-content">
                <ul>
                    <li><strong>What is Prefect?</strong> A modern workflow orchestration platform</li>
                    <li><strong>Purpose:</strong> Build, run, and monitor data pipelines at scale</li>
                    <li><strong>Philosophy:</strong> "Negative engineering" - eliminate workflow failures</li>
                    <li><strong>Key Focus:</strong> Developer experience and operational simplicity</li>
                </ul>
                <div class="highlight-box">
                    <p><em>"The easiest way to coordinate your data stack"</em></p>
                </div>
            </div>
            """
        },
        {
            "number": "002", 
            "title": "Core Capabilities",
            "content": """
            <h1>🛠️ Core Capabilities</h1>
            <div class="slide-content">
                <div class="two-column">
                    <div class="column">
                        <h3>Workflow Management</h3>
                        <ul>
                            <li>Dynamic workflow generation</li>
                            <li>Conditional branching</li>
                            <li>Parallel execution</li>
                            <li>Retry mechanisms</li>
                        </ul>
                        
                        <h3>Monitoring & Observability</h3>
                        <ul>
                            <li>Real-time dashboard</li>
                            <li>Detailed logging</li>
                            <li>Performance metrics</li>
                            <li>Alert notifications</li>
                        </ul>
                    </div>
                    <div class="column">
                        <h3>Infrastructure</h3>
                        <ul>
                            <li>Kubernetes native</li>
                            <li>Docker support</li>
                            <li>Cloud integrations</li>
                            <li>Hybrid deployments</li>
                        </ul>
                        
                        <h3>Developer Experience</h3>
                        <ul>
                            <li>Pure Python workflows</li>
                            <li>Type safety</li>
                            <li>Testing framework</li>
                            <li>Version control integration</li>
                        </ul>
                    </div>
                </div>
            </div>
            """
        },
        {
            "number": "003",
            "title": "Quick Setup",
            "content": """
            <h1>⚡ Quick Setup</h1>
            <div class="slide-content">
                <h3>1. Installation</h3>
                <div class="code-block">
                    <pre><code># Install Prefect
pip install prefect

# Or with extras
pip install "prefect[dev,kubernetes]"</code></pre>
                </div>
                
                <h3>2. First Flow</h3>
                <div class="code-block">
                    <pre><code>from prefect import flow, task

@task
def say_hello(name: str) -> str:
    return f"Hello, {name}!"

@flow
def hello_world():
    greeting = say_hello("Prefect")
    print(greeting)

if __name__ == "__main__":
    hello_world()</code></pre>
                </div>
                
                <h3>3. Run It</h3>
                <div class="code-block">
                    <pre><code>python hello_flow.py</code></pre>
                </div>
            </div>
            """
        },
        {
            "number": "004",
            "title": "Dynamic Workflows",
            "content": """
            <h1>🔄 Dynamic Workflows</h1>
            <div class="slide-content">
                <h3>Key Features</h3>
                <ul>
                    <li><strong>Runtime Generation:</strong> Create workflows based on data</li>
                    <li><strong>Conditional Logic:</strong> Branch based on results</li>
                    <li><strong>Parameter Mapping:</strong> Process lists dynamically</li>
                    <li><strong>Subflows:</strong> Compose complex workflows</li>
                </ul>
                
                <h3>Example: Dynamic Task Creation</h3>
                <div class="code-block">
                    <pre><code>@flow
def dynamic_workflow(items: list):
    results = []
    for item in items:
        if item > 10:
            result = process_large_item(item)
        else:
            result = process_small_item(item)
        results.append(result)
    return combine_results(results)</code></pre>
                </div>
                
                <div class="highlight-box">
                    <p><strong>Advantage:</strong> No need to pre-define all possible workflow paths</p>
                </div>
            </div>
            """
        },
        {
            "number": "005",
            "title": "Task Management",
            "content": """
            <h1>📋 Task Management</h1>
            <div class="slide-content">
                <h3>Task Features</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Execution Control</h4>
                        <ul>
                            <li>Retries with backoff</li>
                            <li>Timeouts</li>
                            <li>Caching</li>
                            <li>Concurrency limits</li>
                        </ul>
                        
                        <h4>Resource Management</h4>
                        <ul>
                            <li>Memory limits</li>
                            <li>CPU requirements</li>
                            <li>Infrastructure blocks</li>
                            <li>Secrets management</li>
                        </ul>
                    </div>
                    <div class="column">
                        <div class="code-block">
                            <pre><code>@task(
    retries=3,
    retry_delay_seconds=60,
    timeout_seconds=300,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def robust_task(data):
    # Task implementation
    return process_data(data)</code></pre>
                        </div>
                    </div>
                </div>
                
                <h3>Task States</h3>
                <p>Pending → Running → Completed/Failed → Cached</p>
            </div>
            """
        },
        {
            "number": "006",
            "title": "Deployment & Scheduling",
            "content": """
            <h1>🚀 Deployment & Scheduling</h1>
            <div class="slide-content">
                <h3>Deployment Options</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Local Development</h4>
                        <ul>
                            <li>Process-based execution</li>
                            <li>SQLite backend</li>
                            <li>File system storage</li>
                        </ul>
                        
                        <h4>Production</h4>
                        <ul>
                            <li>Kubernetes deployments</li>
                            <li>Docker containers</li>
                            <li>Cloud services (AWS, GCP, Azure)</li>
                            <li>Prefect Cloud</li>
                        </ul>
                    </div>
                    <div class="column">
                        <div class="code-block">
                            <pre><code># Create deployment
prefect deployment build ./flow.py:my_flow \\
  --name "production-flow" \\
  --schedule "0 6 * * *" \\
  --work-queue "production"

# Apply deployment
prefect deployment apply my_flow-deployment.yaml

# Start agent
prefect agent start --work-queue "production"</code></pre>
                        </div>
                    </div>
                </div>
                
                <h3>Scheduling Types</h3>
                <ul>
                    <li><strong>Cron:</strong> Traditional cron expressions</li>
                    <li><strong>Interval:</strong> Fixed time intervals</li>
                    <li><strong>RRule:</strong> Complex recurrence rules</li>
                </ul>
            </div>
            """
        },
        {
            "number": "007",
            "title": "Monitoring & Observability",
            "content": """
            <h1>👁️ Monitoring & Observability</h1>
            <div class="slide-content">
                <h3>Prefect UI Dashboard</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Real-time Visibility</h4>
                        <ul>
                            <li>Flow run states</li>
                            <li>Task execution timeline</li>
                            <li>Resource utilization</li>
                            <li>Error tracking</li>
                        </ul>
                        
                        <h4>Historical Analytics</h4>
                        <ul>
                            <li>Success/failure rates</li>
                            <li>Performance trends</li>
                            <li>Duration metrics</li>
                            <li>Cost analysis</li>
                        </ul>
                    </div>
                    <div class="column">
                        <h4>Alerting & Notifications</h4>
                        <ul>
                            <li>Slack integration</li>
                            <li>Email notifications</li>
                            <li>Webhook callbacks</li>
                            <li>Custom notification blocks</li>
                        </ul>
                        
                        <div class="code-block">
                            <pre><code>from prefect.blocks.notifications import SlackWebhook

slack = SlackWebhook.load("my-slack-block")

@flow
def monitored_flow():
    try:
        result = risky_task()
        slack.notify("✅ Flow completed successfully")
    except Exception as e:
        slack.notify(f"❌ Flow failed: {e}")
        raise</code></pre>
                        </div>
                    </div>
                </div>
            </div>
            """
        },
        {
            "number": "008",
            "title": "Integration Ecosystem",
            "content": """
            <h1>🔌 Integration Ecosystem</h1>
            <div class="slide-content">
                <h3>Prefect Collections</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Data Platforms</h4>
                        <ul>
                            <li>AWS (S3, Lambda, ECS)</li>
                            <li>GCP (BigQuery, Cloud Run)</li>
                            <li>Azure (Blob, Functions)</li>
                            <li>Snowflake, Databricks</li>
                        </ul>
                        
                        <h4>Databases</h4>
                        <ul>
                            <li>PostgreSQL, MySQL</li>
                            <li>MongoDB, Redis</li>
                            <li>SQLite, DuckDB</li>
                        </ul>
                    </div>
                    <div class="column">
                        <h4>Infrastructure</h4>
                        <ul>
                            <li>Kubernetes</li>
                            <li>Docker</li>
                            <li>Terraform</li>
                            <li>GitHub Actions</li>
                        </ul>
                        
                        <h4>ML/AI Platforms</h4>
                        <ul>
                            <li>MLflow</li>
                            <li>Weights & Biases</li>
                            <li>Hugging Face</li>
                            <li>OpenAI</li>
                        </ul>
                    </div>
                </div>
                
                <div class="code-block">
                    <pre><code># Example: AWS S3 integration
from prefect_aws import S3Bucket

s3_bucket = S3Bucket.load("my-bucket")

@task
def process_s3_data():
    data = s3_bucket.read_path("input/data.csv")
    processed = transform_data(data)
    s3_bucket.write_path("output/result.csv", processed)</code></pre>
                </div>
            </div>
            """
        },
        {
            "number": "009",
            "title": "Error Handling & Recovery",
            "content": """
            <h1>🛡️ Error Handling & Recovery</h1>
            <div class="slide-content">
                <h3>Built-in Resilience</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Automatic Recovery</h4>
                        <ul>
                            <li>Configurable retries</li>
                            <li>Exponential backoff</li>
                            <li>Circuit breakers</li>
                            <li>Graceful degradation</li>
                        </ul>
                        
                        <h4>Error Classification</h4>
                        <ul>
                            <li>Transient vs permanent</li>
                            <li>Upstream dependencies</li>
                            <li>Resource constraints</li>
                            <li>Data quality issues</li>
                        </ul>
                    </div>
                    <div class="column">
                        <div class="code-block">
                            <pre><code>@task(
    retries=3,
    retry_delay_seconds=[60, 300, 900],
    retry_condition_fn=lambda task, task_run, state: 
        "connection" in str(state.message).lower()
)
def resilient_api_call():
    try:
        return api_client.fetch_data()
    except ConnectionError:
        # Will be retried
        raise
    except ValidationError:
        # Won't be retried
        raise Abort("Invalid data format")</code></pre>
                        </div>
                    </div>
                </div>
                
                <h3>Recovery Strategies</h3>
                <ul>
                    <li><strong>Restart from failure:</strong> Resume where left off</li>
                    <li><strong>Skip failed tasks:</strong> Continue with available data</li>
                    <li><strong>Rollback transactions:</strong> Maintain data consistency</li>
                    <li><strong>Alternative paths:</strong> Fallback workflows</li>
                </ul>
            </div>
            """
        },
        {
            "number": "010",
            "title": "Best Practices",
            "content": """
            <h1>⭐ Best Practices</h1>
            <div class="slide-content">
                <h3>Development Guidelines</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Flow Design</h4>
                        <ul>
                            <li>Keep flows focused and cohesive</li>
                            <li>Use meaningful names</li>
                            <li>Document parameters</li>
                            <li>Version your flows</li>
                        </ul>
                        
                        <h4>Task Organization</h4>
                        <ul>
                            <li>Single responsibility principle</li>
                            <li>Idempotent operations</li>
                            <li>Clear input/output contracts</li>
                            <li>Appropriate granularity</li>
                        </ul>
                    </div>
                    <div class="column">
                        <h4>Testing Strategy</h4>
                        <ul>
                            <li>Unit test individual tasks</li>
                            <li>Integration test flows</li>
                            <li>Mock external dependencies</li>
                            <li>Validate with sample data</li>
                        </ul>
                        
                        <h4>Production Readiness</h4>
                        <ul>
                            <li>Comprehensive logging</li>
                            <li>Resource monitoring</li>
                            <li>Secrets management</li>
                            <li>Disaster recovery plans</li>
                        </ul>
                    </div>
                </div>
                
                <div class="highlight-box">
                    <p><strong>Golden Rule:</strong> Design for failure - assume things will go wrong and plan accordingly</p>
                </div>
            </div>
            """
        },
        
        # Appendix slides (011+)
        {
            "number": "011",
            "title": "Prefect vs Airflow",
            "section": "Appendix",
            "content": """
            <h1>🆚 Prefect vs Apache Airflow</h1>
            <div class="slide-content">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Aspect</th>
                            <th>Prefect</th>
                            <th>Apache Airflow</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Philosophy</strong></td>
                            <td>Negative engineering, eliminate failures</td>
                            <td>Workflow-as-code, maximum control</td>
                        </tr>
                        <tr>
                            <td><strong>Dynamic Workflows</strong></td>
                            <td>✅ Native support</td>
                            <td>⚠️ Limited, requires workarounds</td>
                        </tr>
                        <tr>
                            <td><strong>Learning Curve</strong></td>
                            <td>🟢 Gentle, Pythonic</td>
                            <td>🔴 Steep, many concepts</td>
                        </tr>
                        <tr>
                            <td><strong>UI/UX</strong></td>
                            <td>🟢 Modern, intuitive</td>
                            <td>🟡 Functional but dated</td>
                        </tr>
                        <tr>
                            <td><strong>Development Speed</strong></td>
                            <td>🟢 Fast iteration</td>
                            <td>🟡 Slower due to complexity</td>
                        </tr>
                        <tr>
                            <td><strong>Ecosystem Maturity</strong></td>
                            <td>🟡 Growing rapidly</td>
                            <td>🟢 Very mature, extensive</td>
                        </tr>
                        <tr>
                            <td><strong>Community</strong></td>
                            <td>🟡 Smaller but active</td>
                            <td>🟢 Large, established</td>
                        </tr>
                        <tr>
                            <td><strong>Enterprise Features</strong></td>
                            <td>🟢 Built-in (Prefect Cloud)</td>
                            <td>🟡 Available via Astronomer</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """
        },
        {
            "number": "012",
            "title": "Prefect vs Temporal",
            "section": "Appendix",
            "content": """
            <h1>🆚 Prefect vs Temporal</h1>
            <div class="slide-content">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Aspect</th>
                            <th>Prefect</th>
                            <th>Temporal</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Primary Use Case</strong></td>
                            <td>Data workflows & ETL pipelines</td>
                            <td>Microservice orchestration</td>
                        </tr>
                        <tr>
                            <td><strong>Language Support</strong></td>
                            <td>🟡 Python-first (Go SDK available)</td>
                            <td>🟢 Multi-language (Go, Java, Python, .NET, PHP)</td>
                        </tr>
                        <tr>
                            <td><strong>State Management</strong></td>
                            <td>🟢 Automatic, transparent</td>
                            <td>🟢 Event sourcing, durable</td>
                        </tr>
                        <tr>
                            <td><strong>Debugging</strong></td>
                            <td>🟢 Excellent visibility</td>
                            <td>🟡 Good but complex</td>
                        </tr>
                        <tr>
                            <td><strong>Learning Curve</strong></td>
                            <td>🟢 Gentle</td>
                            <td>🔴 Steep, many abstractions</td>
                        </tr>
                        <tr>
                            <td><strong>Scalability</strong></td>
                            <td>🟢 Excellent for data workloads</td>
                            <td>🟢 Excellent for service workflows</td>
                        </tr>
                        <tr>
                            <td><strong>Data Pipeline Focus</strong></td>
                            <td>🟢 Purpose-built</td>
                            <td>🟡 General purpose</td>
                        </tr>
                        <tr>
                            <td><strong>Setup Complexity</strong></td>
                            <td>🟢 Simple</td>
                            <td>🔴 Complex (requires Temporal Server)</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="highlight-box">
                    <p><strong>When to choose:</strong> Prefect for data workflows, Temporal for microservice orchestration</p>
                </div>
            </div>
            """
        },
        {
            "number": "013",
            "title": "Advanced Features",
            "section": "Appendix",
            "content": """
            <h1>🚀 Advanced Features</h1>
            <div class="slide-content">
                <h3>Prefect Blocks</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Configuration Management</h4>
                        <ul>
                            <li>Reusable configuration objects</li>
                            <li>Type-safe parameters</li>
                            <li>Version controlled</li>
                            <li>Environment-specific configs</li>
                        </ul>
                        
                        <div class="code-block">
                            <pre><code>from prefect.blocks.core import Block

class DatabaseConfig(Block):
    host: str
    port: int = 5432
    database: str
    
    def get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database
        )</code></pre>
                        </div>
                    </div>
                    <div class="column">
                        <h4>Work Pools & Queues</h4>
                        <ul>
                            <li>Resource isolation</li>
                            <li>Priority scheduling</li>
                            <li>Automatic scaling</li>
                            <li>Multi-cloud deployment</li>
                        </ul>
                        
                        <h4>Artifacts & Results</h4>
                        <ul>
                            <li>Persist task outputs</li>
                            <li>Structured metadata</li>
                            <li>Link to external systems</li>
                            <li>Data lineage tracking</li>
                        </ul>
                    </div>
                </div>
                
                <h3>Subflows & Flow Composition</h3>
                <div class="code-block">
                    <pre><code>@flow
def data_ingestion_flow():
    return extract_and_validate_data()

@flow
def transformation_flow(data):
    return transform_and_enrich(data)

@flow
def main_pipeline():
    raw_data = data_ingestion_flow()
    processed_data = transformation_flow(raw_data)
    load_to_warehouse(processed_data)</code></pre>
                </div>
            </div>
            """
        },
        {
            "number": "014",
            "title": "Prefect Cloud Features",
            "section": "Appendix",
            "content": """
            <h1>☁️ Prefect Cloud Features</h1>
            <div class="slide-content">
                <h3>Enterprise-Grade Platform</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Collaboration</h4>
                        <ul>
                            <li>Multi-user workspaces</li>
                            <li>Role-based access control</li>
                            <li>Team management</li>
                            <li>Shared resources</li>
                        </ul>
                        
                        <h4>Compliance & Security</h4>
                        <ul>
                            <li>SOC 2 Type II certified</li>
                            <li>SAML/SSO integration</li>
                            <li>Audit logging</li>
                            <li>Data encryption</li>
                        </ul>
                    </div>
                    <div class="column">
                        <h4>Operational Excellence</h4>
                        <ul>
                            <li>99.9% uptime SLA</li>
                            <li>Global CDN</li>
                            <li>Automated backups</li>
                            <li>24/7 monitoring</li>
                        </ul>
                        
                        <h4>Advanced Analytics</h4>
                        <ul>
                            <li>Custom dashboards</li>
                            <li>Cost optimization insights</li>
                            <li>Performance analytics</li>
                            <li>Data export APIs</li>
                        </ul>
                    </div>
                </div>
                
                <h3>Hybrid Architecture</h3>
                <div class="highlight-box">
                    <p><strong>Control Plane:</strong> Prefect Cloud manages orchestration, UI, and metadata</p>
                    <p><strong>Data Plane:</strong> Your infrastructure executes workloads - data never leaves your environment</p>
                </div>
                
                <h3>Pricing Tiers</h3>
                <ul>
                    <li><strong>Personal:</strong> Free for individuals</li>
                    <li><strong>Pro:</strong> $39/month for small teams</li>
                    <li><strong>Enterprise:</strong> Custom pricing for large organizations</li>
                </ul>
            </div>
            """
        },
        {
            "number": "015",
            "title": "Migration Strategies",
            "section": "Appendix",
            "content": """
            <h1>🔄 Migration Strategies</h1>
            <div class="slide-content">
                <h3>From Airflow to Prefect</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Assessment Phase</h4>
                        <ul>
                            <li>Inventory existing DAGs</li>
                            <li>Identify dependencies</li>
                            <li>Map custom operators</li>
                            <li>Analyze scheduling patterns</li>
                        </ul>
                        
                        <h4>Conversion Process</h4>
                        <ul>
                            <li>DAGs → Flows</li>
                            <li>Tasks remain similar</li>
                            <li>Operators → Task functions</li>
                            <li>XComs → Return values</li>
                        </ul>
                    </div>
                    <div class="column">
                        <div class="code-block">
                            <pre><code># Airflow DAG
from airflow import DAG
from airflow.operators.python import PythonOperator

dag = DAG('my_dag', schedule='@daily')

task1 = PythonOperator(
    task_id='extract',
    python_callable=extract_data,
    dag=dag
)

# Prefect Flow
from prefect import flow, task

@task
def extract_data():
    # Same function
    pass

@flow(schedule="0 0 * * *")
def my_flow():
    extract_data()</code></pre>
                        </div>
                    </div>
                </div>
                
                <h3>Migration Approaches</h3>
                <ul>
                    <li><strong>Big Bang:</strong> Convert all workflows at once</li>
                    <li><strong>Gradual:</strong> Migrate workflows incrementally</li>
                    <li><strong>Parallel:</strong> Run both systems during transition</li>
                    <li><strong>Greenfield:</strong> Start fresh with new workflows</li>
                </ul>
                
                <div class="highlight-box">
                    <p><strong>Pro Tip:</strong> Start with least critical workflows to gain confidence</p>
                </div>
            </div>
            """
        },
        {
            "number": "016",
            "title": "Performance & Scalability",
            "section": "Appendix",
            "content": """
            <h1>📈 Performance & Scalability</h1>
            <div class="slide-content">
                <h3>Scalability Patterns</h3>
                <div class="two-column">
                    <div class="column">
                        <h4>Horizontal Scaling</h4>
                        <ul>
                            <li>Multiple agents per work queue</li>
                            <li>Distributed task execution</li>
                            <li>Auto-scaling based on load</li>
                            <li>Cross-region deployments</li>
                        </ul>
                        
                        <h4>Resource Optimization</h4>
                        <ul>
                            <li>Task concurrency limits</li>
                            <li>Memory-efficient caching</li>
                            <li>Lazy loading strategies</li>
                            <li>Connection pooling</li>
                        </ul>
                    </div>
                    <div class="column">
                        <div class="code-block">
                            <pre><code># Concurrency control
@task(task_run_name="process-{item}")
async def process_item(item):
    return await heavy_computation(item)

@flow(task_runner=ConcurrentTaskRunner())
async def parallel_processing():
    items = get_work_items()
    
    # Process up to 10 items concurrently
    results = await asyncio.gather(*[
        process_item(item) 
        for item in items[:10]
    ])
    
    return results</code></pre>
                        </div>
                    </div>
                </div>
                
                