#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
    CallToolRequestSchema,
    ErrorCode,
    ListToolsRequestSchema,
    McpError,
} from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

const SERPER_API_KEY = process.env.SERPER_API_KEY;
const BROWSERLESS_API_KEY = process.env.BROWSERLESS_API_KEY;
const HUGGINGFACE_API_KEY = process.env.HUGGINGFACE_API_KEY;

if (!SERPER_API_KEY) {
    throw new Error('SERPER_API_KEY environment variable is required');
}
if (!BROWSERLESS_API_KEY) {
    throw new Error('BROWSERLESS_API_KEY environment variable is required');
}
if (!HUGGINGFACE_API_KEY) {
    throw new Error('HUGGINGFACE_API_KEY environment variable is required');
}

const isValidSearchArgs = (
    args: any
): args is { query: string } =>
    typeof args === 'object' &&
    args !== null &&
    typeof args.query === 'string';

const isValidExtractArgs = (
    args: any
): args is { url: string } =>
    typeof args === 'object' &&
    args !== null &&
    typeof args.url === 'string';

const isValidAnalyzeArgs = (
    args: any
): args is { text: string } =>
    typeof args === 'object' &&
    args !== null &&
    typeof args.text === 'string';

class PropertyScoutServer {
    private server: Server;
    private axiosInstance;

    constructor() {
        this.server = new Server(
            {
                name: 'property-scout-server',
                version: '0.1.0',
            },
            {
                capabilities: {
                    tools: {},
                },
            }
        );

        this.axiosInstance = axios.create();

        this.setupToolHandlers();

        this.server.onerror = (error) => console.error('[MCP Error]', error);
        process.on('SIGINT', async () => {
            await this.server.close();
            process.exit(0);
        });
    }

    private setupToolHandlers() {
        this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
            tools: [
                {
                    name: 'search_properties',
                    description: 'Search for properties using Google search via Serper API',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            query: {
                                type: 'string',
                                description: 'Search query for properties',
                            },
                        },
                        required: ['query'],
                    },
                },
                {
                    name: 'extract_property_data',
                    description: 'Extract property data from a webpage using Browserless',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            url: {
                                type: 'string',
                                description: 'URL of the property listing page',
                            },
                        },
                        required: ['url'],
                    },
                },
                {
                    name: 'analyze_properties',
                    description: 'Analyze property data using Hugging Face',
                    inputSchema: {
                        type: 'object',
                        properties: {
                            text: {
                                type: 'string',
                                description: 'Property data text to analyze',
                            },
                        },
                        required: ['text'],
                    },
                },
            ],
        }));

        this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
            if (request.params.name === 'search_properties') {
                if (!isValidSearchArgs(request.params.arguments)) {
                    throw new McpError(
                        ErrorCode.InvalidParams,
                        'Invalid search arguments'
                    );
                }

                const query = request.params.arguments.query;

                try {
                    const response = await this.axiosInstance.post(
                        'https://google.serper.dev/search',
                        {
                            q: query,
                            num: 10,
                        },
                        {
                            headers: {
                                'X-API-KEY': SERPER_API_KEY,
                                'Content-Type': 'application/json',
                            },
                        }
                    );

                    return {
                        content: [
                            {
                                type: 'text',
                                text: JSON.stringify(response.data, null, 2),
                            },
                        ],
                    };
                } catch (error) {
                    if (axios.isAxiosError(error)) {
                        return {
                            content: [
                                {
                                    type: 'text',
                                    text: `Serper API error: ${error.response?.data.message ?? error.message
                                        }`,
                                },
                            ],
                            isError: true,
                        };
                    }
                    throw error;
                }
            } else if (request.params.name === 'extract_property_data') {
                if (!isValidExtractArgs(request.params.arguments)) {
                    throw new McpError(
                        ErrorCode.InvalidParams,
                        'Invalid extract arguments'
                    );
                }

                const url = request.params.arguments.url;

                try {
                    const response = await this.axiosInstance.post(
                        `https://chrome.browserless.io/content?token=${BROWSERLESS_API_KEY}`,
                        {
                            url: url,
                            waitFor: 2000,
                            gotoOptions: { waitUntil: 'networkidle0' },
                        },
                        {
                            headers: {
                                'Content-Type': 'application/json',
                            },
                        }
                    );

                    return {
                        content: [
                            {
                                type: 'text',
                                text: response.data,
                            },
                        ],
                    };
                } catch (error) {
                    if (axios.isAxiosError(error)) {
                        return {
                            content: [
                                {
                                    type: 'text',
                                    text: `Browserless API error: ${error.response?.data.message ?? error.message
                                        }`,
                                },
                            ],
                            isError: true,
                        };
                    }
                    throw error;
                }
            } else if (request.params.name === 'analyze_properties') {
                if (!isValidAnalyzeArgs(request.params.arguments)) {
                    throw new McpError(
                        ErrorCode.InvalidParams,
                        'Invalid analyze arguments'
                    );
                }

                const text = request.params.arguments.text;

                try {
                    const response = await this.axiosInstance.post(
                        'https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english',
                        {
                            inputs: text,
                        },
                        {
                            headers: {
                                'Authorization': `Bearer ${HUGGINGFACE_API_KEY}`,
                                'Content-Type': 'application/json',
                            },
                        }
                    );

                    return {
                        content: [
                            {
                                type: 'text',
                                text: JSON.stringify(response.data, null, 2),
                            },
                        ],
                    };
                } catch (error) {
                    if (axios.isAxiosError(error)) {
                        return {
                            content: [
                                {
                                    type: 'text',
                                    text: `Hugging Face API error: ${error.response?.data.message ?? error.message
                                        }`,
                                },
                            ],
                            isError: true,
                        };
                    }
                    throw error;
                }
            } else {
                throw new McpError(
                    ErrorCode.MethodNotFound,
                    `Unknown tool: ${request.params.name}`
                );
            }
        });
    }

    async run() {
        const transport = new StdioServerTransport();
        await this.server.connect(transport);
        console.error('Property Scout MCP server running on stdio');
    }
}

const server = new PropertyScoutServer();
server.run().catch(console.error);
