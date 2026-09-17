import React, { useState } from 'react';
import { ShieldCheck, ExternalLink, CheckCircle2, Lock, Loader2, BookOpen } from 'lucide-react';
import { toast } from 'sonner';
import { API_CONFIG } from '../services/endpoints';

const AiContentNoticeModal = ({ isOpen, onAccept }) => {
  const [hasReadPolicy, setHasReadPolicy] = useState(false);
  const [isChecked, setIsChecked] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handlePolicyClick = () => {
    setHasReadPolicy(true);
  };

  const handleConfirm = async () => {
    if (!hasReadPolicy || !isChecked) return;
    
    setIsSubmitting(true);
    const consentVal = 'yes';
    try {
      const consentData = {
        accepted: true,
        ai_consent: consentVal,
        timestamp: new Date().toISOString(),
        version: '1.0'
      };

      // 1. Save consent locally
      localStorage.setItem('draftmate_ai_consent_accepted', 'true');
      localStorage.setItem('draftmate_ai_consent_value', consentVal);
      localStorage.setItem('draftmate_ai_consent_details', JSON.stringify(consentData));

      try {
        const profile = JSON.parse(localStorage.getItem('user_profile') || '{}');
        profile.ai_consent = consentVal;
        localStorage.setItem('user_profile', JSON.stringify(profile));
      } catch (e) {}

      // 2. Persist in PostgreSQL users table via auth service
      const sessionId = localStorage.getItem('session_id') || localStorage.getItem('token');
      const userProfile = JSON.parse(localStorage.getItem('user_profile') || '{}');
      const userId = userProfile.id || userProfile.user_id || localStorage.getItem('user_id');

      if (sessionId || userId) {
        try {
          const consentUrl = `${API_CONFIG.AUTH.BASE_URL}/v2/user/consent`;
          await fetch(consentUrl, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${sessionId || ''}`
            },
            body: JSON.stringify({
              user_id: userId || null,
              consent: consentVal
            })
          });
        } catch (apiErr) {
          console.warn('Backend consent sync warning (saved locally):', apiErr);
        }
      }

      window.dispatchEvent(new Event('draftmate_consent_updated'));
      toast.success('Privacy Policy & AI Terms Acknowledged.');
      if (onAccept) onAccept(consentData);
    } catch (err) {
      console.error('Error saving consent:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[99999] flex items-center justify-center bg-slate-900/80 backdrop-blur-md p-4 sm:p-6 animate-in fade-in duration-200">
      <div 
        className="relative w-full max-w-lg rounded-2xl bg-white shadow-[0_25px_70px_rgba(15,23,42,0.35)] border border-slate-200 overflow-hidden flex flex-col my-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Top Accent Header Bar */}
        <div className="bg-gradient-to-r from-blue-700 via-indigo-700 to-blue-800 px-6 py-4 flex items-center gap-3 text-white shadow-md">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-white/15 backdrop-blur-md border border-white/20">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              Privacy Policy & Terms Notice
            </h2>
            <p className="text-xs text-blue-100 font-medium">
              Mandatory Platform Policy Acknowledgment
            </p>
          </div>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-5 max-h-[75vh] overflow-y-auto">
          
          {/* Step 1: Mandatory Link Notice */}
          <div className={`rounded-xl border p-4 transition-all ${
            hasReadPolicy 
              ? 'border-emerald-200 bg-emerald-50/60 text-emerald-950' 
              : 'border-blue-200 bg-blue-50/60 text-blue-950'
          }`}>
            <div className="flex items-start gap-3">
              <BookOpen className={`h-5 w-5 shrink-0 mt-0.5 ${hasReadPolicy ? 'text-emerald-600' : 'text-blue-600'}`} />
              <div className="space-y-2 text-xs leading-relaxed">
                <span className="font-bold uppercase tracking-wider block text-[11px]">
                  Step 1: Read Platform Policies
                </span>
                <p className="text-slate-700 text-xs">
                  Please click and review our Privacy Policy and Terms of Service below to unlock the acknowledgment checkbox.
                </p>

                <div className="pt-1 flex flex-wrap gap-2">
                  <a
                    href="/privacy-policy"
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={handlePolicyClick}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-blue-300 text-blue-700 font-semibold hover:bg-blue-50 transition-all text-xs shadow-sm hover:shadow"
                  >
                    <span>Read Privacy Policy & Terms</span>
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>

                {hasReadPolicy && (
                  <p className="text-emerald-700 font-medium flex items-center gap-1 text-[11px] pt-1">
                    <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600" />
                    <span>Privacy Policy viewed! Checkbox unlocked below.</span>
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Step 2: Checkbox (Disabled until link is clicked) */}
          <div className={`rounded-xl border p-4 transition-all ${
            !hasReadPolicy 
              ? 'border-slate-200 bg-slate-100/60 opacity-65 cursor-not-allowed' 
              : 'border-slate-200 bg-slate-50/80 hover:border-blue-300'
          }`}>
            <label className={`flex items-start gap-3 select-none ${
              !hasReadPolicy ? 'cursor-not-allowed' : 'cursor-pointer'
            }`}>
              <input
                type="checkbox"
                disabled={!hasReadPolicy}
                checked={isChecked}
                onChange={(e) => setIsChecked(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-slate-300 text-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-1 shrink-0 accent-blue-600 disabled:cursor-not-allowed"
              />
              <div className="space-y-1">
                <span className="font-bold text-slate-900 text-xs uppercase tracking-wider block">
                  Step 2: Acknowledgment <span className="text-red-500">*</span>
                </span>
                <p className="text-slate-700 text-xs leading-relaxed">
                  I acknowledge that I have read the <strong>Privacy Policy & Terms</strong>, and I understand that DraftMate AI outputs require human verification before use.
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Modal Footer Controls */}
        <div className="bg-slate-50 border-t border-slate-100 px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5 text-[11px] text-slate-500 font-medium">
            <Lock className="h-3.5 w-3.5 text-slate-400" />
            <span>
              {!hasReadPolicy 
                ? 'Click Privacy Policy link above to unlock' 
                : !isChecked 
                ? 'Check agreement box to proceed' 
                : 'Ready to proceed'}
            </span>
          </div>

          <button
            type="button"
            onClick={handleConfirm}
            disabled={!hasReadPolicy || !isChecked || isSubmitting}
            className={`flex items-center gap-2 rounded-xl px-5 py-2.5 text-sm font-semibold transition-all shadow-md ${
              hasReadPolicy && isChecked
                ? 'bg-blue-600 hover:bg-blue-700 text-white shadow-blue-500/20 active:scale-[0.98]'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed border border-slate-300/60 shadow-none'
            }`}
          >
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 animate-spin text-white" />
            ) : (
              <CheckCircle2 className="h-4 w-4" />
            )}
            <span>{isSubmitting ? 'Saving...' : 'Accept & Proceed'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AiContentNoticeModal;

