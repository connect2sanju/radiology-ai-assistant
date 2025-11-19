import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './index.css'

const API_BASE_URL = 'http://localhost:8000'

function App() {
  const [image, setImage] = useState(null)
  const [imagePreview, setImagePreview] = useState(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [explanations, setExplanations] = useState(null)
  const [accuracyMetrics, setAccuracyMetrics] = useState(null)
  const [analytics, setAnalytics] = useState(null)
  const [analyticsLoading, setAnalyticsLoading] = useState(false)
  const [adminDashboardExpanded, setAdminDashboardExpanded] = useState(false) // Collapsed by default
  const [activeTab, setActiveTab] = useState('report')
  const [editing, setEditing] = useState(false)
  const [editedReport, setEditedReport] = useState(null)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)

  const handleImageUpload = (e) => {
    const file = e.target.files[0]
    if (file) {
      setImage(file)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
      setReport(null)
      setError(null)
      setSuccess(null)
      setAccuracyMetrics(null)
    }
  }

  const generateReport = async () => {
    if (!image) {
      setError('Please upload an image first')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const formData = new FormData()
      formData.append('file', image)

      const response = await axios.post(`${API_BASE_URL}/api/generate-report`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data.success) {
        setReport(response.data.report)
        setExplanations(response.data.explanations)
        setAccuracyMetrics(response.data.accuracy_metrics)
        setEditedReport(null)
        setSuccess('Report generated successfully!')
        setActiveTab('report')
        // Auto-load analytics when report is generated
        fetchAnalytics()
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Error generating report')
    } finally {
      setLoading(false)
    }
  }

  const saveFeedback = async () => {
    if (!report) {
      setError('No report to save')
      return
    }

    // Check if there are actual edits
    if (!editedReport) {
      setError('No changes detected. Please make edits before saving.')
      return
    }

    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const feedbackData = {
        image_name: image?.name || 'uploaded_image.jpg',
        original_report: report,
        edited_report: editedReport,
        explanations: explanations || null,
        ontology_mapping: null, // Can be added if needed
        user_feedback: {}
      }

      const response = await axios.post(`${API_BASE_URL}/api/save-feedback`, feedbackData, {
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.data.success) {
        setSuccess(`Feedback saved successfully! ${response.data.edit_count || 0} edit(s) logged. The model will learn from your corrections.`)
        setEditing(false)
        // Refresh analytics to show updated stats
        setTimeout(() => {
          fetchAnalytics()
        }, 500)
      }
    } catch (err) {
      const errorMsg = err.response?.data?.detail || err.message || 'Error saving feedback'
      setError(errorMsg)
      console.error('Save feedback error:', err)
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = () => {
    if (!report) return

    const displayReport = editedReport || report
    
    // Format report for download
    let reportText = '='.repeat(60) + '\n'
    reportText += 'RADIOLOGY REPORT\n'
    reportText += '='.repeat(60) + '\n\n'
    reportText += `Generated: ${new Date().toLocaleString()}\n`
    reportText += `Image: ${image?.name || 'uploaded_image.jpg'}\n\n`
    
    reportText += 'FINDINGS:\n'
    reportText += '-'.repeat(60) + '\n'
    if (displayReport.findings && displayReport.findings.length > 0) {
      displayReport.findings.forEach((finding, idx) => {
        reportText += `\n${idx + 1}. ${finding.finding}\n`
        reportText += `   Location: ${finding.location || 'N/A'}\n`
        reportText += `   Severity: ${finding.severity || 'N/A'}\n`
        reportText += `   Confidence: ${(finding.confidence * 100).toFixed(1)}%\n`
        reportText += `   Evidence: ${finding.evidence}\n`
      })
    } else {
      reportText += 'No significant findings detected.\n'
    }
    
    reportText += '\n\nIMPRESSION:\n'
    reportText += '-'.repeat(60) + '\n'
    reportText += `${displayReport.impression || 'No impression provided.'}\n`
    
    if (displayReport.recommendations && displayReport.recommendations.length > 0) {
      reportText += '\n\nRECOMMENDATIONS:\n'
      reportText += '-'.repeat(60) + '\n'
      displayReport.recommendations.forEach((rec, idx) => {
        reportText += `${idx + 1}. ${rec}\n`
      })
    }

    // Add accuracy metrics if available
    if (accuracyMetrics) {
      reportText += '\n\nACCURACY METRICS:\n'
      reportText += '-'.repeat(60) + '\n'
      reportText += `Accuracy: ${(accuracyMetrics.accuracy * 100).toFixed(1)}%\n`
      reportText += `Precision: ${(accuracyMetrics.precision * 100).toFixed(1)}%\n`
      reportText += `Recall: ${(accuracyMetrics.recall * 100).toFixed(1)}%\n`
      reportText += `F1 Score: ${(accuracyMetrics.f1_score * 100).toFixed(1)}%\n`
      reportText += `Matched Labels: ${accuracyMetrics.matched_labels.join(', ') || 'None'}\n`
      if (accuracyMetrics.missed_labels.length > 0) {
        reportText += `Missed Labels: ${accuracyMetrics.missed_labels.join(', ')}\n`
      }
    }

    reportText += '\n' + '='.repeat(60) + '\n'
    reportText += 'End of Report\n'
    reportText += '='.repeat(60)

    // Create blob and download
    const blob = new Blob([reportText], { type: 'text/plain' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `radiology_report_${new Date().toISOString().split('T')[0]}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  }

  const getConfidenceClass = (confidence) => {
    if (confidence >= 0.7) return 'confidence-high'
    if (confidence >= 0.4) return 'confidence-medium'
    return 'confidence-low'
  }

  const getAccuracyColor = (value) => {
    if (value >= 0.8) return '#4CAF50'
    if (value >= 0.6) return '#FF9800'
    return '#F44336'
  }

  const fetchAnalytics = async () => {
    setAnalyticsLoading(true)
    try {
      const response = await axios.get(`${API_BASE_URL}/api/analytics`)
      if (response.data.success) {
        setAnalytics(response.data.analytics)
      }
    } catch (err) {
      console.error('Error fetching analytics:', err)
    } finally {
      setAnalyticsLoading(false)
    }
  }

  // Load analytics on component mount and whenever needed
  useEffect(() => {
    fetchAnalytics()
  }, [])

  const displayReport = editedReport || report

  return (
    <div className="app-container">
      <div className="header-section">
        <h1 className="main-header">🏥 Radiology AI Assistant</h1>
        <p className="subtitle">AI-Powered Chest X-Ray Analysis with Explainability</p>
      </div>
      
      <div className="main-layout">
        <div className="content-container">
        {/* Analytics Overview - First Level Info */}
        <div className="analytics-always-visible">
          {analyticsLoading ? (
            <div className="loading">🔄 Loading analytics...</div>
          ) : analytics ? (
            <div className="analytics-container">
              {/* Summary Section */}
              <div className="analytics-section">
                <h3>📊 Summary Statistics</h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-label">Total Reports</div>
                    <div className="stat-value">{analytics.summary?.total_reports || 0}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Total Findings</div>
                    <div className="stat-value">{analytics.summary?.total_findings || 0}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Unique Images</div>
                    <div className="stat-value">{analytics.summary?.unique_images || 0}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Reports with Edits</div>
                    <div className="stat-value">{analytics.summary?.reports_with_edits || 0}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Learning Entries</div>
                    <div className="stat-value">{analytics.summary?.total_learning_entries || 0}</div>
                  </div>
                </div>
              </div>

            </div>
          ) : (
            <div className="no-analytics">
              <p>No analytics data available yet.</p>
              <p>Generate some reports to see analytics.</p>
            </div>
          )}
        </div>

        {/* Upload Section */}
        <div className="card upload-card">
          <div className="card-header">
            <h2>📤 Upload Chest X-Ray Image</h2>
          </div>
          
          <div className="upload-area">
            <input
              type="file"
              accept="image/jpeg,image/jpg,image/png"
              onChange={handleImageUpload}
              className="input-file"
              id="file-upload"
            />
            <label htmlFor="file-upload" className="file-upload-label">
              {image ? 'Change Image' : 'Choose X-Ray Image'}
            </label>
            
            {imagePreview && (
              <div className="image-preview-container">
                <img src={imagePreview} alt="X-Ray Preview" className="image-preview" />
                <p className="image-name">{image?.name}</p>
              </div>
            )}
            
            <button
              onClick={generateReport}
              disabled={!image || loading}
              className="button button-primary generate-btn"
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Generating Report...
                </>
              ) : (
                <>
                  🔬 Generate Radiology Report
                </>
              )}
            </button>
          </div>
          
          {error && <div className="alert alert-error">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}
        </div>

        {/* Results Section */}
        {displayReport && (
          <div className="card results-card">
            <div className="card-header">
              <h2>📋 Diagnostic Report</h2>
              <div className="header-actions">
                <button
                  onClick={downloadReport}
                  className="button button-download"
                  title="Download Report"
                >
                  📥 Download Report
                </button>
              </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
              <button
                className={`tab ${activeTab === 'report' ? 'active' : ''}`}
                onClick={() => setActiveTab('report')}
              >
                📝 Report
              </button>
              <button
                className={`tab ${activeTab === 'findings' ? 'active' : ''}`}
                onClick={() => setActiveTab('findings')}
              >
                🔍 Findings
              </button>
              <button
                className={`tab ${activeTab === 'explanations' ? 'active' : ''}`}
                onClick={() => setActiveTab('explanations')}
              >
                🧠 Explainability
              </button>
            </div>

            {/* Report Tab */}
            {activeTab === 'report' && (
              <div className="tab-content active">
                <div className="report-section">
                  <h3>Clinical Impression</h3>
                  <div className="report-text">
                    {editing ? (
                      <textarea
                        value={displayReport.impression}
                        onChange={(e) => {
                          const updated = JSON.parse(JSON.stringify(displayReport))
                          updated.impression = e.target.value
                          setEditedReport(updated)
                        }}
                        className="report-textarea"
                        rows="4"
                      />
                    ) : (
                      <p>{displayReport.impression || 'No impression provided.'}</p>
                    )}
                  </div>
                </div>

                {displayReport.recommendations && displayReport.recommendations.length > 0 && (
                  <div className="report-section">
                    <h3>Recommendations</h3>
                    <ul className="recommendations-list">
                      {displayReport.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="report-actions">
                  {!editing ? (
                    <button
                      onClick={() => setEditing(true)}
                      className="button button-edit"
                    >
                      ✏️ Edit Report
                    </button>
                  ) : (
                    <div className="edit-actions">
                      <button
                        onClick={() => {
                          setEditing(false)
                          setEditedReport(null)
                        }}
                        className="button"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={saveFeedback}
                        className="button button-primary"
                      >
                        💾 Save Changes
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Findings Tab */}
            {activeTab === 'findings' && (
              <div className="tab-content active">
                <h3>Detailed Findings</h3>
                {displayReport.findings && displayReport.findings.length > 0 ? (
                  <div className="findings-list">
                    {displayReport.findings.map((finding, index) => (
                      <div key={index} className="finding-card">
                        <div className="finding-header">
                          <h4>
                            {editing ? (
                              <input
                                type="text"
                                value={finding.finding}
                                onChange={(e) => {
                                  if (!editedReport) {
                                    setEditedReport(JSON.parse(JSON.stringify(report)))
                                  }
                                  const updated = JSON.parse(JSON.stringify(editedReport || report))
                                  updated.findings[index].finding = e.target.value
                                  setEditedReport(updated)
                                }}
                                className="finding-input"
                              />
                            ) : (
                              finding.finding
                            )}
                          </h4>
                          {editing ? (
                            <div className="confidence-edit">
                              <input
                                type="number"
                                min="0"
                                max="100"
                                step="1"
                                value={(finding.confidence * 100).toFixed(0)}
                                onChange={(e) => {
                                  if (!editedReport) {
                                    setEditedReport(JSON.parse(JSON.stringify(report)))
                                  }
                                  const updated = JSON.parse(JSON.stringify(editedReport || report))
                                  const confidenceValue = Math.max(0, Math.min(100, parseFloat(e.target.value) || 0)) / 100
                                  updated.findings[index].confidence = confidenceValue
                                  setEditedReport(updated)
                                }}
                                className="confidence-input"
                              />
                              <span className="confidence-percent">%</span>
                            </div>
                          ) : (
                            <span className={`confidence-badge ${getConfidenceClass(finding.confidence)}`}>
                              {(finding.confidence * 100).toFixed(0)}%
                            </span>
                          )}
                        </div>
                        
                        <div className="finding-details">
                          <div className="detail-item">
                            <strong>Location:</strong> {finding.location || 'N/A'}
                          </div>
                          <div className="detail-item">
                            <strong>Severity:</strong> {finding.severity || 'N/A'}
                          </div>
                        </div>
                        
                        <div className="finding-evidence">
                          <strong>Evidence:</strong>
                          {editing ? (
                            <textarea
                              value={finding.evidence}
                              onChange={(e) => {
                                if (!editedReport) {
                                  setEditedReport(JSON.parse(JSON.stringify(report)))
                                }
                                const updated = JSON.parse(JSON.stringify(editedReport || report))
                                updated.findings[index].evidence = e.target.value
                                setEditedReport(updated)
                              }}
                              className="evidence-textarea"
                              rows="3"
                            />
                          ) : (
                            <p>{finding.evidence}</p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="no-findings">No findings detected.</p>
                )}
              </div>
            )}

            {/* Explanations Tab */}
            {activeTab === 'explanations' && explanations && (
              <div className="tab-content active">
                {explanations.summary && (
                  <div className="explanation-summary">
                    <h3>Summary</h3>
                    <div className="summary-metrics">
                      <div className="summary-item">
                        <span className="summary-label">Total Findings:</span>
                        <span className="summary-value">{explanations.summary.total_findings}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">High Confidence:</span>
                        <span className="summary-value">{explanations.summary.high_confidence_findings}</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Average Confidence:</span>
                        <span className="summary-value">{(explanations.summary.average_confidence * 100).toFixed(1)}%</span>
                      </div>
                      <div className="summary-item">
                        <span className="summary-label">Reliability:</span>
                        <span className="summary-value">{explanations.summary.overall_reliability.toUpperCase()}</span>
                      </div>
                    </div>
                  </div>
                )}
                
                <h3>Detailed Explanations</h3>
                <div className="explanations-list">
                  {explanations.findings && explanations.findings.map((finding, index) => {
                    const explanation = finding.explanation
                    if (!explanation) return null
                    
                    return (
                      <div key={index} className="explanation-card">
                        <div className="explanation-header">
                          <h4>{finding.finding}</h4>
                          <span className={`confidence-badge ${getConfidenceClass(explanation.confidence_score)}`}>
                            {explanation.confidence_level.toUpperCase()}
                          </span>
                        </div>
                        
                        <div className="explanation-content">
                          <div className="explanation-item">
                            <strong>Confidence Score:</strong> {(explanation.confidence_score * 100).toFixed(1)}%
                          </div>
                          
                          {explanation.evidence_chain && explanation.evidence_chain.length > 0 && (
                            <div className="explanation-item">
                              <strong>Evidence Chain:</strong>
                              <ul className="evidence-chain">
                                {explanation.evidence_chain.map((evidence, idx) => (
                                  <li key={idx}>
                                    <span className="evidence-type">[{evidence.type.toUpperCase()}]</span>
                                    {evidence.description}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {explanation.reasoning && (
                            <div className="explanation-item">
                              <strong>Reasoning:</strong>
                              <p className="reasoning-text">{explanation.reasoning}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {!displayReport && !loading && (
          <div className="card placeholder-card">
            <p className="placeholder-text">
              👈 Upload a chest X-ray image and click 'Generate Radiology Report' to begin analysis
            </p>
          </div>
        )}

        {/* Admin Dashboard - Bottom Section */}
        {analytics?.admin_dashboard && (
          <div className="admin-dashboard-bottom">
            <div className="admin-dashboard-header" onClick={() => setAdminDashboardExpanded(!adminDashboardExpanded)}>
              <h3>👨‍💼 Admin Dashboard</h3>
              <button className="dashboard-toggle">
                {adminDashboardExpanded ? '▼' : '▲'}
              </button>
            </div>
            
            {adminDashboardExpanded && (
              <div className="admin-dashboard-content">
                {/* Operations Breakdown */}
                {analytics.admin_dashboard.operations_breakdown && (
                  <div className="dashboard-section">
                    <h4>Operations Overview</h4>
                    <div className="operations-grid">
                      <div className="operation-card automated">
                        <div className="operation-icon">🤖</div>
                        <div className="operation-label">Automated</div>
                        <div className="operation-value">
                          {analytics.admin_dashboard.operations_breakdown.automated_operations || 0}
                        </div>
                        <div className="operation-percentage">
                          {analytics.admin_dashboard.operations_breakdown.automation_rate}%
                        </div>
                      </div>
                      <div className="operation-card manual">
                        <div className="operation-icon">✋</div>
                        <div className="operation-label">Manual</div>
                        <div className="operation-value">
                          {analytics.admin_dashboard.operations_breakdown.manual_interventions || 0}
                        </div>
                        <div className="operation-percentage">
                          {analytics.admin_dashboard.operations_breakdown.manual_intervention_rate}%
                        </div>
                      </div>
                      <div className="operation-card total">
                        <div className="operation-icon">📊</div>
                        <div className="operation-label">Total</div>
                        <div className="operation-value">
                          {analytics.admin_dashboard.operations_breakdown.total_operations || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Time Period Statistics */}
                {analytics.admin_dashboard.time_period_stats && (
                  <div className="dashboard-section">
                    <h4>Activity by Period</h4>
                    <div className="time-stats">
                      <div className="time-stat-item">
                        <div className="time-stat-label">Today</div>
                        <div className="time-stat-value">{analytics.admin_dashboard.time_period_stats.today?.total || 0}</div>
                        <div className="time-stat-detail">
                          {analytics.admin_dashboard.time_period_stats.today?.automated || 0} auto, {analytics.admin_dashboard.time_period_stats.today?.manual || 0} manual
                        </div>
                      </div>
                      <div className="time-stat-item">
                        <div className="time-stat-label">This Week</div>
                        <div className="time-stat-value">{analytics.admin_dashboard.time_period_stats.this_week?.total || 0}</div>
                        <div className="time-stat-detail">
                          {analytics.admin_dashboard.time_period_stats.this_week?.automated || 0} auto, {analytics.admin_dashboard.time_period_stats.this_week?.manual || 0} manual
                        </div>
                      </div>
                      <div className="time-stat-item">
                        <div className="time-stat-label">This Month</div>
                        <div className="time-stat-value">{analytics.admin_dashboard.time_period_stats.this_month?.total || 0}</div>
                        <div className="time-stat-detail">
                          {analytics.admin_dashboard.time_period_stats.this_month?.automated || 0} auto, {analytics.admin_dashboard.time_period_stats.this_month?.manual || 0} manual
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Performance Metrics */}
                {analytics.admin_dashboard.performance_metrics && (
                  <div className="dashboard-section">
                    <h4>Performance Metrics</h4>
                    <div className="performance-stats">
                      <div className="performance-stat">
                        <div className="performance-label">Avg Confidence</div>
                        <div className="performance-value">
                          {analytics.admin_dashboard.performance_metrics.average_confidence_score || 0}%
                        </div>
                      </div>
                      <div className="performance-stat">
                        <div className="performance-label">Findings/Report</div>
                        <div className="performance-value">
                          {analytics.admin_dashboard.performance_metrics.average_findings_per_report || 0}
                        </div>
                      </div>
                      <div className="performance-stat">
                        <div className="performance-label">Reports/Day</div>
                        <div className="performance-value">
                          {analytics.admin_dashboard.performance_metrics.reports_per_day_avg || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Manual Interventions */}
                {analytics.admin_dashboard.manual_interventions && analytics.admin_dashboard.manual_interventions.total_interventions > 0 && (
                  <div className="dashboard-section">
                    <h4>Manual Interventions</h4>
                    <div className="intervention-stats">
                      <div className="intervention-stat">
                        <strong>Total:</strong> {analytics.admin_dashboard.manual_interventions.total_interventions}
                      </div>
                      <div className="intervention-stat">
                        <strong>Avg Edits:</strong> {analytics.admin_dashboard.manual_interventions.average_edits_per_intervention}
                      </div>
                    </div>
                    {analytics.admin_dashboard.manual_interventions.recent_interventions && 
                     analytics.admin_dashboard.manual_interventions.recent_interventions.length > 0 && (
                      <div className="interventions-list">
                        <h5>Recent</h5>
                        {analytics.admin_dashboard.manual_interventions.recent_interventions.slice(0, 5).map((intervention, idx) => (
                          <div key={idx} className="intervention-item">
                            <div className="intervention-header">
                              <span className="intervention-image">{intervention.image?.substring(0, 20) || 'Unknown'}</span>
                              <span className="intervention-count">{intervention.edit_count} edits</span>
                            </div>
                            <div className="intervention-time">
                              {intervention.timestamp ? new Date(intervention.timestamp).toLocaleDateString() : 'N/A'}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
        </div>
      </div>
    </div>
  )
}

export default App
