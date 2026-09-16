# Project Initial Details Submission — Workplace Safety Assessment Logging System

## 1. Problem Statement and Target Users

### Problem Statement

Singapore's construction industry has a tight deadline to meet, leaving little room for unforeseen circumstances. Despite national workplace fatality rates hitting a record low of 0.96 per 100,000 workers in 2025, construction remained the largest contributor to serious injury: 148 fatal and major injuries (24% of the national total), a rate 1.5 times the all-industry average, and more lost man-days than any other sector (Ministry of Manpower, Singapore, 2026).

Falls from height were the leading cause, followed by vehicular incidents, struck-by-falling-object incidents, and caught-in/between-object incidents. These are all "Type A" incidents which carry a higher fatality risk. MOM attributes most of these incidents to inadequate risk assessments, lack of worker competency, and unsafe behaviours that have not been properly addressed (Ministry of Manpower, Singapore, 2026).

All these points not to the lack of safety awareness, but to a lack of on-the-ground visibility when the hazard is happening. This shows how safety reporting works today: manual, inconsistent, reporting it on WhatsApp, paper forms, or just memory. The current safety reporting methods burden the site manager, who must weigh the risk of the reported incident against the deadline of the respective construction project without any real-time data. Without a system that gives immediate, prioritised hazard visibility, high-risk incidents can go unaddressed simply because managers lack the information to identify which ones need urgent attention.

The objective of this system is to give Workplace Safety & Health officers and site supervisors a real-time, prioritised overview of the logged hazards, so that review effort and stop-work decisions focus on the high-risk incidents first.

### Target Users

- Site supervisors, who log incidents as they happen.
- Workplace Safety & Health (WSH) officers, who review logged incidents and decide on escalation.

## 2. User Inputs

Supervisors enter the following through a terminal-based prompt when logging an incident:

- **Incident description:** A description of what happened (e.g. "worker slipped near the scaffolding, no injury, wet floor").
- **Location:** The worksite or area where it happened.
- **Reporter role:** Who's submitting the report.
- **Injury flag:** Whether anyone was injured (yes/no).

## 3. Use of AI

### How AI Is Used

The AI is used to gather supporting evidence, not to make the final call. When the supervisor logs an incident, the `ai_manager` checks the hazard type to see which real-world data will be relevant to the incident reported. If the hazard is related to the weather, it will then call the weather API using the incident's location to get the current conditions like rain, temperature, humidity, and PSI level. For other types of hazard like electrical or chemical, it will then provide general data that is relevant to the hazard. If the API call fails, the `ai_manager` does not guess the data — it will log the error, then log the incident without the external data, and flag it for review.

The `ai_manager` does not classify or give judgement on the incident; it will only fetch and validate the external data. Once the external data is retrieved, the `ai_manager` will keep the original incident description together with the external data gathered into one enriched record, and it will then pass this information to the `logic_manager`. This shows that the `ai_manager` contains zero domain logic, as its job is just to build the prompt, call the API, parse the response, and validate the response.

### Outputs and How They're Used

The AI's output is the enriched record, which consists of the original incident report and the relevant external data (like the weather conditions), keeping the original report so nothing is overwritten. The `ai_manager` does not classify hazard type, severity, or recurrence likelihood, as that judgment is made by `logic_manager` using this enriched record.

The final judgment on what happens next will be handled by the `logic_manager`'s fixed business rules, and ultimately by a human reviewer, not the AI.

Lastly, at the end of every month, the AI will collate a report based on the incidents to spread awareness and reduce workplace incidents.

## 4. Business Rules

The `logic_manager` is the one that will judge each of the AI-enriched incident records, applying the following rules to get the outcome.

The `logic_manager` first determines the hazard type, severity, and recurrence likelihood using the original description as well as the external data the `ai_manager` has attached. The `logic_manager` takes the supporting evidence given by the `ai_manager` into a judgement. Once the assessment is made, the `logic_manager` will apply the following rules:

- **Rule 1 (severity):** If (severity ≥ 4) OR (injury = yes AND recurrence likelihood = high), then stop-work review.
- **Rule 2 (recurring likelihood):** The same location flagged 3 or more times within 30 days then escalates as a systemic risk.
- **Default:** If neither rule fires, the incident is saved as a low priority record.

Before the rules run, the system checks that the incident record has everything the `logic_manager` needs to make its assessment, to make sure nothing is wrong or missing. If one of the fields is missing or the value does not make sense, it will try again once. If it still fails, the incident will be flagged as pending review instead of the system creating an assumption. This way, every incident reported is treated equally, based on the same assessment process before a decision is made.

Ultimately, this system is not meant to replace the judgement of a Workplace Safety officer or site supervisor, but to help them decide what to review first.

## Repository Information

**GitHub repository URL:** [https://github.com/INF1103team6/inf1103project1.git](https://github.com/INF1103team6/inf1103project1.git)

## References

Ministry of Manpower, Singapore. (2026). *Workplace safety and health report 2025 – National statistics*. https://www.mom.gov.sg/-/media/mom/documents/safety-health/reports-stats/wsh-national-statistics/wsh-national-stats-2025.pdf
