import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { MemoryClient, Message } from 'mem0ai';
import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

// Session configuration schema (used by Smithery CLI for HTTP/StreamableHTTP)
export const configSchema = z.object({
  mem0ApiKey: z
    .string()
    .describe('Mem0 API key. Defaults to MEM0_API_KEY env var if not provided.'),
  defaultUserId: z
    .string()
    .optional()
    .default('mem0-mcp-user')
    .describe("Default user ID when not provided in tool input"),
});

// Factory to create the MCP server. Smithery CLI will call this for HTTP transport.
export default function createServer({
  config,
}: {
  config: z.infer<typeof configSchema>;
}) {
  const apiKey = config.mem0ApiKey || process?.env?.MEM0_API_KEY || '';
  const defaultUserId = config.defaultUserId || 'mem0-mcp-user';

  const memoryClient = new MemoryClient({ apiKey });

  const server = new McpServer({
    name: 'mem0-mcp',
    version: '0.0.1',
  });

  // add-memory tool
  server.tool(
    'add-memory',
    'Add a new memory about the user. Call this whenever the user shares preferences, facts about themselves, or explicitly asks you to remember something.',
    {
      content: z.string().describe('The content to store in memory'),
      userId: z
        .string()
        .optional()
        .describe("User ID for memory storage. If omitted, uses config.defaultUserId."),
    },
    async ({ content, userId }) => {
      const resolvedUserId = userId || defaultUserId;
      try {
        const messages: Message[] = [
          { role: 'user', content: content }
        ];
        memoryClient.add(messages, { user_id: resolvedUserId, async_mode: true, version: "v2", output_format: "v1.1" });
        return {
          content: [
            {
              type: 'text',
              text: 'Memory added successfully',
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text:
                'Error adding memory: ' +
                (error instanceof Error ? error.message : String(error)),
            },
          ],
          isError: true,
        } as const;
      }
    }
  );

  // search-memories tool
  server.tool(
    'search-memories',
    'Search through stored memories. Call this whenever you need to recall prior information relevant to the user query.',
    {
      query: z
        .string()
        .describe(
          "The search query, typically derived from the user's current question."
        ),
      userId: z
        .string()
        .optional()
        .describe("User ID for memory storage. If omitted, uses config.defaultUserId."),
    },
    async ({ query, userId }) => {
      const resolvedUserId = userId || defaultUserId;
      try {
        const results: any[] = await memoryClient.search(query, {
          user_id: resolvedUserId,
        });
        const formattedResults = (results || [])
          .map((result: any) => `Memory: ${result.memory}\nRelevance: ${result.score}\n---`)
          .join('\n');

        return {
          content: [
            {
              type: 'text',
              text: formattedResults || 'No memories found',
            },
          ],
        };
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text:
                'Error searching memories: ' +
                (error instanceof Error ? error.message : String(error)),
            },
          ],
          isError: true,
        } as const;
      }
    }
  );

  return server.server;
}

// Optional: keep STDIO compatibility for local usage
async function main() {
  try {
    console.error('Initializing Mem0 Memory MCP Server (stdio mode)...');

    const server = createServer({
      config: {
        mem0ApiKey: process?.env?.MEM0_API_KEY,
        defaultUserId: process?.env?.DEFAULT_USER_ID || 'mem0-mcp-user',
      },
    });

    const transport = new StdioServerTransport();
    await server.connect(transport);

    console.error('Memory MCP Server running on stdio');
  } catch (error) {
    console.error('Fatal error running server:', error);
    process.exit(1);
  }
}

// Execute main when launched directly via node dist/index.js
if (process.argv[1] && process.argv[1].includes('index.js')) {
  // best-effort detection; avoids executing during smithery-cli runtime
  main().catch((error) => {
    console.error('Fatal error in main():', error);
    process.exit(1);
  });
}
