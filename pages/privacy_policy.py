# pages/privacy_policy.py
import dash
from dash import html, callback, Input, Output

dash.register_page(
    __name__,
    path="/privacy_policy",
    name="Privacy Policy",
)

layout = html.Div(
    [
        html.Div(id="privacy-policy-body-content", style={"flex": "1"}),

        html.Footer(
            children=[
                html.Hr(),
                html.Div(
                    [
                        html.P(
                            "This site is not affiliated with the Department of Defense. I am an NCO who got tired of remaking spreadsheets to speculate about points.",
                            className="mb-0",
                            style={"color": "yellow"},
                        ),
                        html.P(
                            "Contact: PromotionPointDashboard@gmail.com",
                            className="mb-0",
                            style={"color": "yellow"},
                        ),
                        html.P(
                            "© 2026 Army Promotion Point Dashboard",
                            className="mb-0",
                            style={"color": "yellow"},
                        ),
                    ],
                    className="text-center",
                ),
                html.Div(style={"height": "40px"}),
            ],
            style={
                "backgroundColor": "#013220",
                "padding": "0px",
                "width": "100%",
            },
        ),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "minHeight": "100vh",
    },
)


@callback(
    Output("privacy-policy-body-content", "children"),
    Input("dark-mode-store", "data"),
    allow_duplicate=True,
)
def update_privacy_policy_text(is_dark):
    text_color = "white" if is_dark else "black"

    body_container_style = {
        "maxWidth": "980px",
        "marginLeft": "auto",
        "marginRight": "auto",
        "paddingLeft": "24px",
        "paddingRight": "24px",
        "paddingTop": "30px",
        "paddingBottom": "30px",
        "fontFamily": "Arial, sans-serif",
    }

    h1_style = {
        "color": "gold",
        "textAlign": "center",
        "fontFamily": "Georgia, serif",
        "marginBottom": "0.5em",
    }

    h2_style = {
        "color": "green",
        "marginTop": "2em",
        "fontFamily": "Georgia, serif",
    }

    h3_style = {"marginTop": "1em", "fontFamily": "Georgia, serif"}

    p_style = {
        "fontSize": "18px",
        "marginBottom": "1.25em",
        "lineHeight": "1.7",
        "color": text_color,
    }

    li_span_style = {"fontSize": "18px", "color": text_color}

    link_style = {"color": "green", "textDecoration": "underline", "fontSize": "18px"}

    return html.Div(
        [
            html.H1("Privacy Policy", style=h1_style),
            html.P(
                "Last updated: February 25, 2026",
                style={
                    "textAlign": "center",
                    "color": text_color,
                    "fontStyle": "italic",
                    "fontSize": "18px",
                    "marginBottom": "2em",
                    "fontFamily": "Arial, sans-serif",
                },
            ),
            html.P(
                "This Privacy Policy explains what information may be processed when you use this website, why it may be processed, and what choices you have. "
                "The goal is clarity. This site exists to display Army promotion point trend visuals and supporting tables. "
                "I do not ask you to create an account and I do not intentionally collect personal information from you for my own use.",
                style=p_style,
            ),
            html.P(
                [
                    "Important note: this site is hosted and delivered using third party services including ",
                    html.Strong("Cloudflare"),
                    " and ",
                    html.Strong("Railway"),
                    ". Like most websites, those services may process limited technical data to deliver pages, protect against abuse, and keep the service reliable. "
                    "This policy describes those categories in plain language.",
                ],
                style=p_style,
            ),
            html.H2("Who We Are", style=h2_style),
            html.P(
                [
                    html.Strong("Site name: "),
                    html.Span("Army Promotion Point Dashboard", style=li_span_style),
                ],
                style=p_style,
            ),
            html.P(
                [
                    html.Strong("Website: "),
                    html.A(
                        "https://promotionpointdashboard.com/",
                        href="https://promotionpointdashboard.com/",
                        target="_blank",
                        style=link_style,
                    ),
                ],
                style=p_style,
            ),
            html.P(
                [
                    html.Strong("Contact email: "),
                    html.A(
                        "promotionpointdashboard@gmail.com",
                        href="mailto:promotionpointdashboard@gmail.com",
                        style={"textDecoration": "underline", "fontSize": "18px", "color": text_color},
                    ),
                ],
                style=p_style,
            ),
            html.H2("Interpretation and Definitions", style=h2_style),
            html.H3("Interpretation", style=h3_style),
            html.P(
                "Words with initial capitalization have meanings defined below. These definitions apply whether the terms appear in singular or plural.",
                style=p_style,
            ),
            html.H3("Definitions", style=h3_style),
            html.P("For the purposes of this Privacy Policy:", style=p_style),
            html.Ul(
                [
                    html.Li(
                        [
                            html.Strong("Company, We, Us, Our: "),
                            html.Span("refers to the operator of Army Promotion Point Dashboard.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Country: "),
                            html.Span("United States of America.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Device: "),
                            html.Span("any device that can access the Service, such as a computer, phone, or tablet.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Personal Data: "),
                            html.Span("information that relates to an identified or identifiable individual.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Service: "),
                            html.Span("the website and related pages served at promotionpointdashboard.com.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Service Provider: "),
                            html.Span("a third party that processes data to deliver hosting, security, analytics, or related infrastructure.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Usage Data: "),
                            html.Span("technical data that may be collected automatically when you access the Service.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("You: "),
                            html.Span("the individual accessing the Service, or the entity on whose behalf the Service is accessed.", style=li_span_style),
                        ]
                    ),
                ],
                style={"marginBottom": "2em", "lineHeight": "1.7"},
            ),
            html.H2("Summary of What We Collect", style=h2_style),
            html.P(
                "This site does not provide user accounts and does not request your name, phone number, mailing address, or payment details. "
                "However, the infrastructure used to deliver the site may process limited technical data that is typical for websites.",
                style=p_style,
            ),
            html.H3("Usage Data (technical data)", style=h3_style),
            html.P(
                "Usage Data may include information such as your IP address, browser type, device type, operating system, pages visited, timestamps, and basic diagnostic data. "
                "This data is commonly used to deliver pages, prevent abuse, and troubleshoot reliability issues.",
                style=p_style,
            ),
            html.H3("Cookies and similar technologies", style=h3_style),
            html.P(
                "Cookies are small files stored on your device. They may support security protections, load balancing, and performance optimization. "
                "Some services also use similar technologies such as local storage, pixels, or request headers.",
                style=p_style,
            ),
            html.P(
                "You can control cookies through your browser settings. Disabling cookies may impact the reliability of certain features, including security protections.",
                style=p_style,
            ),
            html.H2("How We Use Information", style=h2_style),
            html.P(
                "Information that may be processed by the Service or its providers is used for the following purposes:",
                style=p_style,
            ),
            html.Ul(
                [
                    html.Li([html.Strong("To provide the Service: "), html.Span("serve pages and site functionality.", style=li_span_style)]),
                    html.Li([html.Strong("To maintain reliability and security: "), html.Span("detect abuse, mitigate attacks, and keep the site available.", style=li_span_style)]),
                    html.Li([html.Strong("To troubleshoot and improve performance: "), html.Span("identify errors, reduce downtime, and improve load times.", style=li_span_style)]),
                    html.Li([html.Strong("To comply with legal obligations: "), html.Span("respond to lawful requests when required.", style=li_span_style)]),
                ],
                style={"marginBottom": "2em", "lineHeight": "1.7"},
            ),
            html.H2("Legal Bases for Processing", style=h2_style),
            html.P(
                "Depending on your location, the legal bases for processing may include legitimate interests (running a secure and reliable website), "
                "your consent (where required for certain cookies), and compliance with legal obligations.",
                style=p_style,
            ),
            html.H2("Service Providers", style=h2_style),
            html.P(
                "We use third party services to host and deliver the website. These providers may process technical data to provide their services.",
                style=p_style,
            ),
            html.Ul(
                [
                    html.Li(
                        [
                            html.Strong("Cloudflare: "),
                            html.Span(
                                "content delivery network and security services that help protect the site and improve performance.",
                                style=li_span_style,
                            ),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("Railway: "),
                            html.Span(
                                "application hosting platform used to run the dashboard server and related services.",
                                style=li_span_style,
                            ),
                        ]
                    ),
                ],
                style={"marginBottom": "1.5em", "lineHeight": "1.7"},
            ),
            html.P(
                [
                    "You should also review the privacy policies of these providers for details about their processing. "
                    "Provider policies control how they handle data as independent companies.",
                ],
                style=p_style,
            ),
            html.H2("Sharing of Information", style=h2_style),
            html.P(
                "We do not sell your personal information. Information may be shared in the following limited situations:",
                style=p_style,
            ),
            html.Ul(
                [
                    html.Li(
                        [
                            html.Strong("With Service Providers: "),
                            html.Span("to operate hosting, security, and site delivery infrastructure.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("For legal compliance: "),
                            html.Span("to comply with applicable law, regulation, or lawful requests.", style=li_span_style),
                        ]
                    ),
                    html.Li(
                        [
                            html.Strong("To protect rights and safety: "),
                            html.Span("to investigate or prevent misuse, fraud, or security incidents.", style=li_span_style),
                        ]
                    ),
                ],
                style={"marginBottom": "2em", "lineHeight": "1.7"},
            ),
            html.H2("Data Retention", style=h2_style),
            html.P(
                "We do not maintain user accounts on this site. Technical logs, if retained by infrastructure providers, are generally kept only as long as needed for security, diagnostics, and operational purposes.",
                style=p_style,
            ),
            html.H2("Your Privacy Rights", style=h2_style),
            html.P(
                "Depending on where you live, you may have rights relating to your personal information, including the right to access, correct, delete, or restrict certain processing. "
                "Because we do not operate user accounts, most requests will relate to provider logs, which may be controlled by the providers.",
                style=p_style,
            ),
            html.P(
                [
                    "If you have a privacy request, contact ",
                    html.A(
                        "promotionpointdashboard@gmail.com",
                        href="mailto:promotionpointdashboard@gmail.com",
                        style={"textDecoration": "underline", "fontSize": "18px", "color": text_color},
                    ),
                    " and describe your request and the approximate time of your visit. We will respond as reasonably and promptly as we can.",
                ],
                style=p_style,
            ),
            html.H2("International Transfers", style=h2_style),
            html.P(
                "Your information may be processed in locations where our Service Providers operate. Data protection laws may differ by jurisdiction.",
                style=p_style,
            ),
            html.H2("Security", style=h2_style),
            html.P(
                "We take reasonable steps to keep the site secure, including the use of reputable hosting and security providers. "
                "No method of transmission or storage is perfectly secure, and we cannot guarantee absolute security.",
                style=p_style,
            ),
            html.H2("Children’s Privacy", style=h2_style),
            html.P(
                "This Service is not intended for children under 13. We do not knowingly collect personal information from children under 13.",
                style=p_style,
            ),
            html.H2("Links to Other Websites", style=h2_style),
            html.P(
                "The Service may link to other websites that are not operated by us. We are not responsible for the content or privacy practices of those sites.",
                style=p_style,
            ),
            html.H2("Changes to This Privacy Policy", style=h2_style),
            html.P(
                "We may update this Privacy Policy from time to time. Updates are effective when posted on this page. "
                "If changes are significant, we will make a reasonable effort to highlight them on the site.",
                style=p_style,
            ),
            html.H2("Contact Us", style=h2_style),
            html.P(
                [
                    "If you have any questions about this Privacy Policy, email ",
                    html.A(
                        "promotionpointdashboard@gmail.com",
                        href="mailto:promotionpointdashboard@gmail.com",
                        style={"textDecoration": "underline", "fontSize": "18px", "color": text_color},
                    ),
                    ".",
                ],
                style=p_style,
            ),
        ],
        style=body_container_style,
    )