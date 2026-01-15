"use client";

import { CopilotKit } from "@copilotkit/react-core";
import { CopilotChat } from "@copilotkit/react-ui";
import "@copilotkit/react-ui/styles.css";

export default function Home() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="openshift_assistant"
    >
      <div className="flex flex-col h-screen">
        {/* Header */}
        <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
          <h1 className="text-2xl font-bold text-white">
            OpenShift AI Assistant
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            Ask questions about Kubernetes and OpenShift
          </p>
        </header>

        {/* Chat Interface */}
        <div className="flex-1 overflow-hidden">
          <CopilotChat
            instructions="You are an expert Kubernetes and OpenShift assistant. Help users understand and troubleshoot their clusters."
            labels={{
              title: "OpenShift Assistant",
              initial: "Hi! I can answer questions about Kubernetes and OpenShift. How can I help you today?",
            }}
            className="h-full"
          />
        </div>
      </div>
    </CopilotKit>
  );
}
