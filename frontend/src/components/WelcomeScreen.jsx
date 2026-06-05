import React from 'react';

export default function WelcomeScreen({ onSelectQuery }) {
  return (
    <section className="w-full max-w-2xl px-md py-xl flex flex-col items-center text-center m-auto" id="welcome-view">
      <div className="w-16 h-16 rounded-full bg-surface-container flex items-center justify-center mb-md border border-outline-variant">
        <span className="material-symbols-outlined text-primary text-[32px]">shield_with_heart</span>
      </div>
      <h2 className="font-headline-lg text-headline-lg mb-sm text-on-surface">Mutual Fund Facts Assistant</h2>
      <p className="font-body-sm text-on-surface-variant max-w-md mb-lg">
        Your high-precision gateway to mutual fund analysis. Ask about fees, exit loads, risk metrics, or specific portfolio holdings.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-sm w-full">
        <button 
          onClick={() => onSelectQuery("What is the exit load of HDFC Mid-Cap Opportunities Fund?")}
          className="flex flex-col items-center gap-xs p-md rounded-lg border border-outline-variant bg-surface-container hover:border-primary-container transition-all group"
        >
          <span className="material-symbols-outlined text-primary group-hover:scale-110 transition-transform">assignment_return</span>
          <span className="font-label-md text-label-md text-on-surface-variant group-hover:text-primary transition-colors">Exit Load Details</span>
        </button>
        <button 
          onClick={() => onSelectQuery("What are the top holdings of HDFC Small Cap Fund?")}
          className="flex flex-col items-center gap-xs p-md rounded-lg border border-outline-variant bg-surface-container hover:border-primary-container transition-all group"
        >
          <span className="material-symbols-outlined text-primary group-hover:scale-110 transition-transform">pie_chart</span>
          <span className="font-label-md text-label-md text-on-surface-variant group-hover:text-primary transition-colors">Top Holdings</span>
        </button>
        <button 
          onClick={() => onSelectQuery("What is the risk assessment of HDFC Multi Cap Fund?")}
          className="flex flex-col items-center gap-xs p-md rounded-lg border border-outline-variant bg-surface-container hover:border-primary-container transition-all group"
        >
          <span className="material-symbols-outlined text-primary group-hover:scale-110 transition-transform">warning</span>
          <span className="font-label-md text-label-md text-on-surface-variant group-hover:text-primary transition-colors">Risk Assessment</span>
        </button>
      </div>
    </section>
  );
}
